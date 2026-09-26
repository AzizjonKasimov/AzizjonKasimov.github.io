# Makes the web images for the site from a certificate scan, a screenshot, or a photo: a full-size
# JPEG and smaller ones for thumbnails and phones. All are re-encoded, so the source's metadata is
# dropped. Writes only to the kind's folder under public/. Safe to re-run.
#
#   .\tools\web-images.ps1 -Kind certificate -Source <scan.pdf|.jpg|.png> -Name <file-name>
#   .\tools\web-images.ps1 -Kind screenshot -Source <image> -Name <file-name>
#   .\tools\web-images.ps1 -Kind photo -Source <image> -Name <file-name>
#
#   certificate  public/certificates/  <name>.jpg (1240 px wide) and <name>-thumb.jpg (400 px)
#   screenshot   public/screenshots/   <name>.jpg (up to 1600 px wide, so small text stays sharp),
#                                      <name>-medium.jpg (960 px, for phones) and <name>-thumb.jpg (480 px)
#   photo        public/images/        <name>.jpg (600 x 600) and <name>-thumb.jpg (300 x 300),
#                                      cut square from the middle of the photo
#
# Images are never enlarged. A PDF must be a one-page scan that holds a single JPEG image, which is
# the usual scanner output. The site is public: cover private details in the source first, such as a
# date of birth, an ID number, or a customer's name.

param(
  [Parameter(Mandatory)] [ValidateSet('certificate', 'screenshot', 'photo')] [string] $Kind,
  [Parameter(Mandatory)] [string] $Source,
  [Parameter(Mandatory)] [ValidatePattern('^[a-z0-9]+(-[a-z0-9]+)*$')] [string] $Name
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$settings = @{
  certificate = @{ Folder = 'certificates'; Square = $false; Jobs = @(@{ Suffix = ''; Width = 1240; Quality = 82 }, @{ Suffix = '-thumb'; Width = 400; Quality = 80 }) }
  screenshot = @{ Folder = 'screenshots'; Square = $false; Jobs = @(@{ Suffix = ''; Width = 1600; Quality = 90 }, @{ Suffix = '-medium'; Width = 960; Quality = 84 }, @{ Suffix = '-thumb'; Width = 480; Quality = 80 }) }
  photo = @{ Folder = 'images'; Square = $true; Jobs = @(@{ Suffix = ''; Width = 600; Quality = 84 }, @{ Suffix = '-thumb'; Width = 300; Quality = 82 }) }
}[$Kind]

$root = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $root "public\$($settings.Folder)"

# Scanned PDFs store the page as one JPEG stream, so read that stream instead of rendering the PDF.
function Read-SourceBytes([string] $path) {
  $bytes = [IO.File]::ReadAllBytes($path)
  if ([IO.Path]::GetExtension($path) -ne '.pdf') { return , $bytes }
  $text = [Text.Encoding]::Latin1.GetString($bytes)
  $found = [regex]::Matches($text, '<<((?:(?!>>).)*?/Subtype\s*/Image(?:(?!>>).)*?)>>\s*stream\r?\n', 'Singleline')
  $dict = if ($found.Count -eq 1) { $found[0].Groups[1].Value } else { '' }
  $length = [regex]::Match($dict, '/Length\s+(\d+)(?!\d)(?!\s+\d+\s+R)')
  if ($dict -notmatch '/Filter\s*/DCTDecode' -or -not $length.Success) {
    throw "$path is not a one-image JPEG scan. Export the page as a PNG or JPEG and pass that instead."
  }
  $jpeg = [byte[]]::new([int]$length.Groups[1].Value)
  [Array]::Copy($bytes, $found[0].Index + $found[0].Length, $jpeg, 0, $jpeg.Length)
  if ($jpeg[0] -ne 0xFF -or $jpeg[1] -ne 0xD8) { throw "Could not read the scan image in $path." }
  return , $jpeg
}

$stream = [IO.MemoryStream]::new((Read-SourceBytes (Resolve-Path $Source).Path))
$image = [Drawing.Image]::FromStream($stream)

# Photos can be stored sideways with an EXIF orientation tag; turn the pixels upright.
if ($image.PropertyIdList -contains 0x0112) {
  $flip = @{ 2 = 'RotateNoneFlipX'; 3 = 'Rotate180FlipNone'; 4 = 'Rotate180FlipX'; 5 = 'Rotate90FlipX'; 6 = 'Rotate90FlipNone'; 7 = 'Rotate270FlipX'; 8 = 'Rotate270FlipNone' }[[int]$image.GetPropertyItem(0x0112).Value[0]]
  if ($flip) { $image.RotateFlip($flip) }
}

# The part of the source to use: all of it, or the largest centered square for a photo.
$crop = [Drawing.Rectangle]::new(0, 0, $image.Width, $image.Height)
if ($settings.Square) {
  $side = [Math]::Min($image.Width, $image.Height)
  $crop = [Drawing.Rectangle]::new([int](($image.Width - $side) / 2), [int](($image.Height - $side) / 2), $side, $side)
}

New-Item -ItemType Directory -Force $outDir | Out-Null
$encoder = [Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg'
foreach ($job in $settings.Jobs) {
  $width = [Math]::Min($job.Width, $crop.Width)
  $height = [int][Math]::Round($crop.Height * $width / $crop.Width)
  $canvas = [Drawing.Bitmap]::new($width, $height, [Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $graphics = [Drawing.Graphics]::FromImage($canvas)
  $graphics.InterpolationMode = 'HighQualityBicubic'
  $graphics.PixelOffsetMode = 'HighQuality'
  # Mirror the edge pixels while resampling; otherwise GDI+ blends a gray line into the border.
  $edges = [Drawing.Imaging.ImageAttributes]::new()
  $edges.SetWrapMode('TileFlipXY')
  $graphics.DrawImage($image, [Drawing.Rectangle]::new(0, 0, $width, $height), $crop.X, $crop.Y, $crop.Width, $crop.Height, [Drawing.GraphicsUnit]::Pixel, $edges)
  $params = [Drawing.Imaging.EncoderParameters]::new(1)
  $params.Param[0] = [Drawing.Imaging.EncoderParameter]::new([Drawing.Imaging.Encoder]::Quality, [long]$job.Quality)
  $output = Join-Path $outDir "$Name$($job.Suffix).jpg"
  $canvas.Save($output, $encoder, $params)
  $graphics.Dispose(); $canvas.Dispose(); $edges.Dispose(); $params.Dispose()
  Write-Host ('Wrote public\{0}\{1} ({2}x{3}, {4:N0} KB)' -f $settings.Folder, (Split-Path -Leaf $output), $width, $height, ((Get-Item $output).Length / 1KB))
}
$image.Dispose(); $stream.Dispose()
