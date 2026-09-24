# Makes the web images of a certificate scan for the homepage gallery: a full-size JPEG to read
# (1240 px wide) and a thumbnail (400 px wide). Both are re-encoded, so the scan's metadata is
# dropped. Writes only to public/certificates/. Safe to re-run.
#
#   .\tools\certificate-images.ps1 -Source <scan.pdf|.jpg|.png> -Name <file-name>
#
# A PDF must be a one-page scan that holds a single JPEG image, which is the usual scanner output.
# The site is public: check the scan for private details, such as a date of birth or an ID number,
# before you run this.

param(
  [Parameter(Mandatory)] [string] $Source,
  [Parameter(Mandatory)] [ValidatePattern('^[a-z0-9]+(-[a-z0-9]+)*$')] [string] $Name
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$root = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $root 'public\certificates'
$jobs = @(
  @{ Suffix = ''; Width = 1240; Quality = 82 },
  @{ Suffix = '-thumb'; Width = 400; Quality = 80 }
)

# Scanned PDFs store the page as one JPEG stream, so read that stream instead of rendering the PDF.
function Read-ScanBytes([string] $path) {
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

$stream = [IO.MemoryStream]::new((Read-ScanBytes (Resolve-Path $Source).Path))
$image = [Drawing.Image]::FromStream($stream)

# Photos can be stored sideways with an EXIF orientation tag; turn the pixels upright.
if ($image.PropertyIdList -contains 0x0112) {
  $flip = @{ 2 = 'RotateNoneFlipX'; 3 = 'Rotate180FlipNone'; 4 = 'Rotate180FlipX'; 5 = 'Rotate90FlipX'; 6 = 'Rotate90FlipNone'; 7 = 'Rotate270FlipX'; 8 = 'Rotate270FlipNone' }[[int]$image.GetPropertyItem(0x0112).Value[0]]
  if ($flip) { $image.RotateFlip($flip) }
}

New-Item -ItemType Directory -Force $outDir | Out-Null
$encoder = [Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg'
foreach ($job in $jobs) {
  $width = [Math]::Min($job.Width, $image.Width)
  $height = [int][Math]::Round($image.Height * $width / $image.Width)
  $canvas = [Drawing.Bitmap]::new($width, $height, [Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $graphics = [Drawing.Graphics]::FromImage($canvas)
  $graphics.InterpolationMode = 'HighQualityBicubic'
  $graphics.PixelOffsetMode = 'HighQuality'
  # Mirror the edge pixels while resampling; otherwise GDI+ blends a gray line into the border.
  $edges = [Drawing.Imaging.ImageAttributes]::new()
  $edges.SetWrapMode('TileFlipXY')
  $graphics.DrawImage($image, [Drawing.Rectangle]::new(0, 0, $width, $height), 0, 0, $image.Width, $image.Height, [Drawing.GraphicsUnit]::Pixel, $edges)
  $params = [Drawing.Imaging.EncoderParameters]::new(1)
  $params.Param[0] = [Drawing.Imaging.EncoderParameter]::new([Drawing.Imaging.Encoder]::Quality, [long]$job.Quality)
  $output = Join-Path $outDir "$Name$($job.Suffix).jpg"
  $canvas.Save($output, $encoder, $params)
  $graphics.Dispose(); $canvas.Dispose(); $edges.Dispose(); $params.Dispose()
  Write-Host ('Wrote public\certificates\{0} ({1}x{2}, {3:N0} KB)' -f (Split-Path -Leaf $output), $width, $height, ((Get-Item $output).Length / 1KB))
}
$image.Dispose(); $stream.Dispose()
