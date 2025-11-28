# Storybooks Directory

This directory contains storybook content files for character-specific knowledge bases using RAG (Retrieval-Augmented Generation).

## Directory Structure

```
storybooks/
├── {conf_uid}/           # Character-specific directory (e.g., example_story_001)
│   ├── story.txt         # Main story content
│   ├── chapter1.md       # Additional chapters or sections
│   ├── characters.txt    # Character descriptions
│   └── world.txt         # World-building details
└── README.md             # This file
```

## Supported File Formats

- **`.txt`**: Plain text files
- **`.md`**: Markdown files
- **`.pdf`**: PDF files (requires PyPDF2, optional)

## How to Use

### 1. Create a Character Directory

Create a directory named after your character's `conf_uid`:

```bash
mkdir storybooks/my_character_001
```

### 2. Add Storybook Content

Add your story content as text or markdown files:

```bash
# Example story content
echo "Once upon a time in the Whispering Woods..." > storybooks/my_character_001/story.txt
```

### 3. Configure Character Settings

In your character configuration file (e.g., `characters/my_character.yaml`):

```yaml
character_config:
  conf_uid: "my_character_001"
  storybook_title: "My Story Title"
  storybook_language: "en"
  target_age_range: "4-7"
  
  rag_config:
    enabled: true
    rag_type: "simple"
    auto_load_storybook: true
    storybook_directory: "storybooks"
    chunk_size: 300
    chunk_overlap: 50
    max_context_docs: 5
```

### 4. Start the Server

When the server starts, it will automatically load all files from `storybooks/{conf_uid}/` and index them for RAG retrieval.

## Content Guidelines

### File Organization

- **Main Story**: Put the core narrative in `story.txt` or `story.md`
- **Chapters**: Split long stories into multiple files (e.g., `chapter1.txt`, `chapter2.txt`)
- **Supporting Content**: Add character descriptions, world-building, etc. in separate files

### Writing Tips

1. **Keep chunks meaningful**: Each paragraph or section should be self-contained
2. **Use clear language**: Match the target age range
3. **Include context**: Add character names, locations, and key details in each section
4. **Avoid very long files**: Split into multiple files if content exceeds 5000 words

### Example Content Structure

```
storybooks/little_fox_001/
├── story.txt              # Main narrative
├── characters.txt         # Character descriptions
├── locations.txt          # Places in the story
└── lessons.txt            # Moral lessons and themes
```

## Chunking Behavior

The system automatically splits your content into chunks for efficient retrieval:

- **Chunk Size**: Configurable (default: 300 words)
- **Overlap**: Configurable (default: 50 words)
- **Strategy**: Sentence-boundary aware splitting

## Troubleshooting

### No documents loaded

- Check that the directory name matches your `conf_uid`
- Verify files have supported extensions (`.txt`, `.md`)
- Check file permissions and encoding (UTF-8 recommended)

### Poor retrieval quality

- Adjust `chunk_size` (try 200-500)
- Adjust `min_score` threshold (try 0.2-0.4)
- Increase `max_context_docs` (try 5-10)
- Add more context to each section

### Character responses feel too modern or out-of-character

- Add more details about the story's time period and setting
- Include more examples of the character's values and worldview
- Enrich the story content with cultural details and customs
- The character will interpret modern concepts through their story lens

## Advanced Usage

### Multiple Languages

You can mix languages in the same directory. The embedding model supports multilingual content.

### Metadata

Files are automatically tagged with metadata:
- `source`: File path
- `filename`: File name
- `chunk_index`: Position in the original file

### Manual Document Loading

If you need to load documents programmatically:

```python
from src.dreamtale.rag.document_loader import load_storybook_documents

documents, metadatas = await load_storybook_documents(
    directory="storybooks/my_character_001",
    chunk_size=300,
    chunk_overlap=50
)

await rag_engine.add_documents(documents, metadatas)
```

## Examples

See the `storybooks/example_story_001/` directory for a complete example.

---

For more information, see `STORYBOOK_MODE.md` in the project root.

