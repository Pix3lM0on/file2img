# file2img

Convert files into images that can be previewed, shared, archived, or decoded
back into the original data.

`file2img` starts with a simple promise: every file can become a picture. Some
files should become useful previews, like text, PDFs, or source code. Any file
should also be able to become a lossless data image that can be restored later.

## Goals

- Turn common files into readable preview images.
- Turn any binary file into a lossless encoded image.
- Restore lossless encoded images back into their original files.
- Provide a small GUI for everyday use and a CLI for scripts.
- Keep conversions predictable, inspectable, and local-first.

## Core Modes

### Preview Mode

Creates a human-readable image from a supported file type.

Examples:

- Text files rendered with line wrapping and optional syntax highlighting.
- Markdown rendered as formatted document pages.
- Source files rendered with monospace text and line numbers.
- Images converted, resized, or reformatted.

Preview mode is useful for sharing or inspecting files, but it is not expected
to preserve every byte of the original input.

### Data Mode

Encodes raw file bytes into pixels.

Data mode should be lossless: the generated image contains enough metadata and
pixel data to reconstruct the original file exactly. This mode is useful for
experiments, archival tricks, and moving arbitrary files through image-only
systems.

## Expected Workflow

1. Choose one or more input files.
2. Choose a conversion mode.
3. Pick output settings such as image format, size, theme, and destination.
4. Generate images.
5. For lossless images, optionally decode them back into files.

## CLI Sketch

```sh
file2img encode input.bin output.png
file2img decode output.png restored.bin
file2img preview notes.md notes.png
```

Useful options might include:

- `--mode preview|data`
- `--format png|webp|jpg`
- `--theme light|dark`
- `--width <pixels>`
- `--metadata`
- `--overwrite`

## GUI Sketch

The first GUI should be practical and small:

- File picker or drag-and-drop area.
- Mode selector for `Preview` and `Data`.
- Output preview panel.
- Conversion settings sidebar.
- Convert, save, and decode actions.
- Status area for errors, warnings, and completed files.

## Supported Formats

Initial target support:

- Any file in data mode.
- Plain text.
- Markdown.
- Common image formats.

Later support:

- PDFs.
- Source code with syntax highlighting.
- Archives with manifest previews.
- Audio files with waveform previews.

## Milestones

### 1. Lossless Data Prototype

- Read a file as bytes.
- Pack bytes into RGB or RGBA pixels.
- Store original filename, size, checksum, and encoding version.
- Decode the image back into the original file.
- Verify round-trip integrity with tests.

### 2. Minimal CLI

- Add `encode` and `decode` commands.
- Support PNG output.
- Print useful errors for invalid inputs.

### 3. Minimal GUI

- Load one file.
- Choose mode.
- Convert to image.
- Save output.

### 4. Preview Renderers

- Add text renderer.
- Add Markdown renderer.
- Add image conversion renderer.

## Design Notes

- PNG should be the default for lossless data images.
- JPEG should never be used for lossless data mode.
- Encoded images should include a small versioned header.
- Decoding should fail clearly when metadata or checksums do not match.
- The program should avoid uploading files anywhere.

## Name

`file2img` is short, literal, and a little suspicious in the right way.
