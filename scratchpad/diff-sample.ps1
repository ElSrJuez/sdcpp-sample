
$body = @{
  model = "z_image_turbo"  # label is accepted; the server uses the model you booted with
  prompt = "A cinematic, melancholic photograph of a solitary hooded figure walking through a sprawling, rain-slicked metropolis at night"
  size = "512x512"
  n = 1
  response_format = "b64_json"
} | ConvertTo-Json

$resp = Invoke-RestMethod `
  -Uri "http://phantom.homenet:4242/v1/images/generations" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

# Save the first image
$img = $resp.data[0].b64_json
[IO.File]::WriteAllBytes(".\out\api_out.png",[Convert]::FromBase64String($img))
