# README assets

The README uses the studio's forest-green, sage, and ivory palette. Keep badges
short and factual, with descriptive alt text and links to the relevant section.
All images live in the repository so private repository pages and extracted
installer archives can display them without an external badge service.

- `lecturebridge-banner.png`: 2172 × 724 editorial illustration, generated with
  the built-in image generation tool. The original generation prompt is in
  [banner-prompt.txt](banner-prompt.txt). It illustrates speech becoming text;
  it is not an application screenshot.
- `studio-preview.png`: actual studio UI captured with synthetic audio/text
  fixtures during browser tests. Contains no classroom recording or personal data.
- `badge-*.svg`: static, project-owned labels. They describe release stage,
  supported platforms, local processing, and the source license. They do not
  report live CI status or model licensing.

Keep the README's textual title, setup instructions, and limitations readable
without the images. Add every README image to the installer builder's explicit
file allowlist when introducing or renaming an asset.
