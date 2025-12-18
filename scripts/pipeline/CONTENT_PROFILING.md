# Content Profiling Implementation

## Overview

Content profiling has been implemented in the Slideforge pipeline based on LibV2 patterns. This provides comprehensive analytics about presentation structure, content quality, and compliance with design guidelines.

## Implementation Details

### 1. PresentationProfile Dataclass

Location: `/home/bacon/Desktop/Slideforge/scripts/pipeline/manifest.py`

The `PresentationProfile` dataclass tracks:

#### Slide Statistics
- `total_slides`: Total number of slides in presentation
- `total_sections`: Number of sections
- `total_words`: Word count across all content
- `total_characters`: Character count across all content

#### Slide Type Distribution
- `slide_type_distribution`: Dict mapping slide types to counts
  - Example: `{"content": 15, "section_header": 5, "title": 1}`

#### Section Analysis
- `section_sizes`: Dict mapping section names to slide counts
  - Example: `{"Introduction": 5, "Main Content": 10}`

#### Content Quality Metrics
- `speaker_notes_coverage`: Percentage of slides with notes (0.0-1.0)
- `average_bullets_per_slide`: Mean bullets across all slides
- `average_words_per_bullet`: Mean words per bullet point
- `six_by_six_compliance`: Percentage of slides following 6x6 rule (0.0-1.0)

#### Content Complexity
- `vocabulary_richness`: Type-token ratio (vocabulary diversity, 0.0-1.0)
- `average_sentence_length`: Mean words per sentence

#### Visual Elements
- `images_count`: Number of image slides
- `tables_count`: Number of table slides
- `charts_count`: Number of chart/data visualization slides

### 2. Profiling Functions

#### extract_presentation_profile(presentation: Dict) -> PresentationProfile

Extracts comprehensive profile from presentation schema JSON.

**Process:**
1. Iterates through all sections and slides
2. Counts slide types and visual elements
3. Extracts all text content for analysis
4. Calculates 6x6 compliance by checking:
   - Bullet count <= 6 per slide
   - Word count <= 12 per bullet
5. Computes vocabulary richness
6. Analyzes sentence structure

**Content Extraction:**
- Titles and subtitles
- Bullet points (main, left, right columns)
- Table headers and rows
- Process steps and timeline events
- Key-value pairs
- Statistics and cards
- Callouts and details
- Speaker notes

#### calculate_vocabulary_richness(texts: List[str]) -> float

Calculates type-token ratio for vocabulary diversity assessment.

**Formula:**
```
TTR = unique_words / total_words
```

Higher values (closer to 1.0) indicate more diverse vocabulary.

#### calculate_content_complexity(presentation: Dict) -> Dict

Assesses content complexity metrics:

**Returns:**
- `average_sentence_length`: Words per sentence
- `vocabulary_diversity`: Type-token ratio
- `reading_level`: Estimated level
  - "basic": avg sentence < 10 words
  - "intermediate": avg sentence 10-20 words
  - "advanced": avg sentence > 20 words

### 3. Integration into Pipeline

Location: `/home/bacon/Desktop/Slideforge/scripts/pipeline/orchestrator.py`

The profiling is integrated into the `_stage_transformation()` method:

```python
# After successful transformation
profile = extract_presentation_profile(presentation)
self.manifest.set_presentation_profile(profile)

# Log summary
logger.info(f"Content profile: {slide_count} slides, "
           f"{profile.total_words} words, "
           f"{profile.six_by_six_compliance*100:.1f}% 6x6 compliance, "
           f"{profile.speaker_notes_coverage*100:.1f}% notes coverage")
```

### 4. Manifest Storage

The profile is automatically stored in the pipeline manifest and serialized to JSON:

```json
{
  "presentationProfile": {
    "totalSlides": 25,
    "totalSections": 5,
    "totalWords": 2500,
    "totalCharacters": 15000,
    "slideTypeDistribution": {
      "content": 15,
      "section_header": 5,
      "title": 1,
      "comparison": 2,
      "table": 2
    },
    "sectionSizes": {
      "Introduction": 5,
      "Main Content": 10,
      "Conclusion": 5
    },
    "speakerNotesCoverage": 0.95,
    "averageBulletsPerSlide": 4.2,
    "averageWordsPerBullet": 6.8,
    "sixBySixCompliance": 0.92,
    "vocabularyRichness": 0.65,
    "averageSentenceLength": 12.3,
    "imagesCount": 3,
    "tablesCount": 2,
    "chartsCount": 1
  }
}
```

## Usage

### Automatic Profiling

Profiling happens automatically during the transformation stage:

```bash
cd scripts/pipeline
python3 -m pipeline.cli input.md output.pptx
```

The profile will be included in the manifest file: `output_manifest.json`

### Manual Profiling

You can also profile a presentation structure directly:

```python
from pipeline.manifest import extract_presentation_profile

presentation = {
    "metadata": {"title": "My Presentation"},
    "sections": [...]
}

profile = extract_presentation_profile(presentation)

print(f"Total slides: {profile.total_slides}")
print(f"6x6 compliance: {profile.six_by_six_compliance:.2%}")
print(f"Notes coverage: {profile.speaker_notes_coverage:.2%}")
```

### Accessing Profile from Manifest

```python
from pipeline.manifest import load_manifest

manifest = load_manifest("output_manifest.json")

if manifest.presentation_profile:
    profile = manifest.presentation_profile
    print(f"Slide types: {profile.slide_type_distribution}")
    print(f"Section sizes: {profile.section_sizes}")
```

## Quality Metrics Interpretation

### 6x6 Compliance

- **1.0 (100%)**: All slides comply with 6x6 rule
- **0.8-0.99**: Mostly compliant, minor violations
- **< 0.8**: Significant violations, content may be too dense

### Speaker Notes Coverage

- **> 0.9**: Excellent coverage, well-documented
- **0.7-0.9**: Good coverage
- **< 0.7**: Poor coverage, consider adding more notes

### Vocabulary Richness

- **> 0.7**: High diversity, rich vocabulary
- **0.5-0.7**: Moderate diversity
- **< 0.5**: Low diversity, repetitive content

### Average Bullets Per Slide

- **< 5**: Good, concise content
- **5-6**: Acceptable, approaching limit
- **> 6**: Too dense, consider splitting slides

### Average Words Per Bullet

- **< 10**: Excellent, very concise
- **10-12**: Good, within guidelines
- **> 12**: Too wordy, needs simplification

## Testing

Comprehensive test suite: `test_content_profiling.py`

Run tests:
```bash
cd scripts/pipeline
python3 test_content_profiling.py
```

Tests cover:
- Profile extraction from sample presentation
- Vocabulary richness calculation
- Content complexity analysis
- Serialization/deserialization

## LibV2 Pattern Compliance

This implementation follows LibV2 content profiling patterns:

1. **Comprehensive Metrics**: Tracks all relevant aspects of content quality
2. **Automatic Generation**: Profiling happens during transformation
3. **Manifest Integration**: Profile stored with provenance data
4. **Complexity Analysis**: Vocabulary and sentence analysis
5. **Quality Scoring**: 6x6 compliance and coverage metrics

## Future Enhancements

Potential improvements:

1. **Reading Level**: More sophisticated readability metrics (Flesch-Kincaid, etc.)
2. **Slide Balance**: Analyze content distribution across sections
3. **Visual Density**: Track image-to-text ratio
4. **Accessibility Metrics**: Alt text coverage, color contrast
5. **Trend Analysis**: Compare profiles across presentation versions
6. **Recommendations**: Automated suggestions for improvement

## Related Files

- `/home/bacon/Desktop/Slideforge/scripts/pipeline/manifest.py` - Profile dataclass and functions
- `/home/bacon/Desktop/Slideforge/scripts/pipeline/orchestrator.py` - Pipeline integration
- `/home/bacon/Desktop/Slideforge/scripts/pipeline/test_content_profiling.py` - Test suite
- `/home/bacon/Desktop/Slideforge/schemas/presentation/presentation_schema.json` - Presentation schema

## References

- LibV2 Content Profiling Patterns
- Slideforge Presentation Schema
- 6x6 Rule for Presentation Design
