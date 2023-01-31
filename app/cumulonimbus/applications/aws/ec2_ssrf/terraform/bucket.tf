resource "random_uuid" "ssrf" {
}

resource "aws_s3_bucket" "ssrf" {
  bucket        = "secret-stuff-${random_uuid.ssrf.result}"
  force_destroy = true
  tags = {
    Name        = "secret-stuff-${random_uuid.ssrf.result}"
    Description = "Secret Recipe Bucket"
  }
}

resource "aws_s3_object" "ssrf" {
  bucket = aws_s3_bucket.ssrf.id
  key    = "secret_recipe.txt"
  source = "../files/secret_recipe.txt"

}

resource "aws_s3_bucket_acl" "secret-s3-bucket-acl" {
  bucket = aws_s3_bucket.ssrf.id
  acl    = "private"
}
