# file2img

Convert files into images.

Right now this is just the start of the project. The first goal is to make a
basic program that can take a file and turn its contents into an image.

## TODO

- [x] Create the project
- [x] Write the first README
- [x] Make the initial commit
- [ ] Decide the first version's language and GUI toolkit
- [ ] Make (working) CLI
- [ ] Make GUI wrapper for the ((maybe) working) CLI
- [ ] Save the generated image

## Example usage

- Converting to image
  ```sh
  file2img encode some_file.mkv output.png
  ```

- Converting back
  ```sh
  file2img decode some_file.png [output]
  ```
  Output name is optional. If you skip it, file2img will try to pull the
  original name from the image metadata.

- Changing defaults
  ```sh
  file2img config set default.pattern "spiral"
  ```

## Patterns
- Default
  - `spiral`
  - `spiral_reverse`
  - `row`
  - `row_reverse`
- File type specific
  - `text`
  - more coming soon?

## Stuff to change with `file2img config`

- default.pattern
  - You can see those above.