#!/usr/bin/env python3
"""Script to append helper methods to orchestrator.py"""

helper_methods = '''
    def _load_checkpoints_until_updated(self, stage_name: str) -> None:
        """Load checkpoint data for stages before the specified stage."""
        if not self.checkpoint_manager:
            return

        stage_idx = self.STAGES.index(stage_name)

        for stage in self.STAGES[:stage_idx]:
            checkpoint = self.checkpoint_manager.get_checkpoint_for_stage(stage)
            if checkpoint:
                self._stage_data.update(checkpoint.state_snapshot)
                self._stage_results.update(checkpoint.stage_results)
                logger.debug(f"Loaded checkpoint for stage: {stage}")

    def _load_from_checkpoint(self, checkpoint_id: str) -> int:
        """
        Load state from checkpoint and return starting stage index.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            Index of stage to resume from
        """
        if not self.checkpoint_manager:
            raise CheckpointError("Checkpoint manager not initialized")

        checkpoint = self.checkpoint_manager.load_checkpoint(checkpoint_id)
        if not checkpoint:
            raise CheckpointError(f"Checkpoint not found: {checkpoint_id}")

        self._load_checkpoint_state(checkpoint)

        # Resume from next stage after checkpoint
        stage_idx = self.STAGES.index(checkpoint.stage)
        return min(stage_idx + 1, len(self.STAGES) - 1)

    def _load_checkpoint_state(self, checkpoint: PipelineCheckpoint) -> None:
        """
        Load pipeline state from checkpoint.

        Args:
            checkpoint: Checkpoint to load from
        """
        self._stage_data = checkpoint.state_snapshot.copy()
        self._stage_results = checkpoint.stage_results.copy()
        self._stages_completed = checkpoint.stages_completed.copy()
        logger.info(f"Loaded checkpoint from {checkpoint.timestamp}, {len(self._stages_completed)} stages completed")

    def _wrap_with_retry(self, func: Callable) -> Callable:
        """
        Wrap a function with retry logic.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with retry logic
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = 1.0

            for attempt in range(self.config.max_retry_attempts):
                try:
                    result = func(*args, **kwargs)

                    # Track recovery if this wasn't first attempt
                    if attempt > 0:
                        self._recovered_errors += 1
                        logger.info(f"Recovered after {attempt} retries")

                    return result

                except RecoverableError as e:
                    last_exception = e
                    if attempt < self.config.max_retry_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{self.config.max_retry_attempts} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= 2.0
                    else:
                        logger.error(f"All {self.config.max_retry_attempts} attempts failed")
                        raise

            if last_exception:
                raise last_exception

            return func(*args, **kwargs)

        return wrapper

    def _handle_stage_failure(
        self,
        stage_name: str,
        stage_result: StageResult,
        pipeline_result: PipelineResult
    ) -> bool:
        """
        Handle stage failure and determine if pipeline can continue.

        Args:
            stage_name: Name of failed stage
            stage_result: Result from failed stage
            pipeline_result: Overall pipeline result

        Returns:
            True if pipeline can continue, False otherwise
        """
        # Critical stages cannot be bypassed
        if stage_name in self._critical_stages:
            logger.error(f"Critical stage {stage_name} failed, cannot continue")

            # Create structured error
            pipeline_error = PipelineError(
                stage=stage_name,
                error_type="CriticalStageFailure",
                message=f"Critical stage '{stage_name}' failed",
                context={
                    'errors': stage_result.errors,
                    'warnings': stage_result.warnings,
                    'duration_ms': stage_result.duration_ms
                },
                recoverable=False,
                suggestions=self._get_failure_suggestions(stage_name, stage_result),
                traceback=None
            )
            pipeline_result.structured_errors.append(pipeline_error)
            pipeline_result.errors.extend(stage_result.errors)

            return False

        # Non-critical stages can use fallbacks
        logger.warning(f"Non-critical stage {stage_name} failed, attempting fallback")

        # Apply fallback based on stage
        if stage_name == 'template_selection':
            # Use default template
            self._stage_data['selected_template'] = 'minimal'
            self.manifest.template_used = 'minimal'
            logger.info("Using default 'minimal' template as fallback")
            return True

        elif stage_name == 'validation':
            # Continue without validation
            logger.warning("Continuing without validation checks")
            return True

        elif stage_name == 'extraction':
            # Try basic extraction
            logger.warning("Semantic extraction failed, attempting basic parsing")
            return False  # For now, treat as critical

        elif stage_name == 'transformation':
            # Cannot continue without transformation
            logger.error("Transformation is required, cannot continue")
            return False

        # Unknown stage - be conservative
        return False

    def _get_failure_suggestions(
        self,
        stage_name: str,
        stage_result: StageResult
    ) -> List[str]:
        """
        Get suggestions for recovering from stage failure.

        Args:
            stage_name: Name of failed stage
            stage_result: Result from failed stage

        Returns:
            List of suggestion strings
        """
        suggestions = []

        if stage_name == 'ingestion':
            suggestions.extend([
                "Check that the input file exists and is readable",
                "Verify the file format is supported (Markdown, HTML, JSON)",
                "Ensure the file is not corrupted or empty"
            ])

        elif stage_name == 'extraction':
            suggestions.extend([
                "Check input content structure and formatting",
                "Try simplifying complex nested structures",
                "Verify content encoding (UTF-8 expected)"
            ])

        elif stage_name == 'transformation':
            suggestions.extend([
                "Review semantic structure for invalid data",
                "Check that all required fields are present",
                "Reduce content complexity if transformation times out"
            ])

        elif stage_name == 'template_selection':
            suggestions.extend([
                "Specify a template explicitly using --template option",
                "Check that template catalog is accessible",
                "Verify template files exist in templates/pptx/"
            ])

        elif stage_name == 'validation':
            suggestions.extend([
                "Review validation errors for specific issues",
                "Use --no-strict to reduce validation strictness",
                "Check slide content against 6x6 rule"
            ])

        elif stage_name == 'generation':
            suggestions.extend([
                "Verify python-pptx is installed correctly",
                "Check that output directory is writable",
                "Ensure presentation structure is valid",
                "Try with a different template"
            ])

        # Add checkpoint resume suggestion
        if self.checkpoint_manager:
            suggestions.append(
                f"Use --resume-from {stage_name} to retry this stage after fixing issues"
            )

        return suggestions

    def _save_partial_results(self, failed_stage: str) -> Path:
        """
        Save partial results when pipeline fails.

        Args:
            failed_stage: Name of stage that failed

        Returns:
            Path to partial results directory
        """
        try:
            output_dir = self.config.output_path.parent
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            partial_dir = output_dir / f"partial_results_{timestamp}"
            partial_dir.mkdir(parents=True, exist_ok=True)

            # Save stage data
            stage_data_path = partial_dir / "stage_data.json"
            with open(stage_data_path, 'w', encoding='utf-8') as f:
                # Convert stage data to JSON-serializable format
                serializable_data = {}
                for key, value in self._stage_data.items():
                    try:
                        json.dumps(value)  # Test if serializable
                        serializable_data[key] = value
                    except (TypeError, ValueError):
                        serializable_data[key] = str(value)

                json.dump(serializable_data, f, indent=2)

            # Save stage results
            results_path = partial_dir / "stage_results.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(self._stage_results, f, indent=2)

            # Save recovery info
            recovery_info = {
                "failedStage": failed_stage,
                "stagesCompleted": self._stages_completed,
                "timestamp": timestamp,
                "recoverySuggestions": [
                    "Review stage_data.json and stage_results.json for debugging",
                    "Fix the underlying issue and retry the pipeline",
                    f"Use --resume-from {failed_stage} to continue from this point",
                    "Check checkpoint files for more detailed state"
                ]
            }

            recovery_path = partial_dir / "recovery_info.json"
            with open(recovery_path, 'w', encoding='utf-8') as f:
                json.dump(recovery_info, f, indent=2)

            logger.info(f"Partial results saved to: {partial_dir}")
            return partial_dir

        except Exception as e:
            logger.error(f"Failed to save partial results: {e}")
            return output_dir / "partial_results_failed"

'''

print("Helper methods ready to append. These should be manually integrated into the Pipeline class.")
print(f"Total lines: {len(helper_methods.splitlines())}")
