resource "random_uuid" "ssrf" {
}

resource "aws_s3_bucket" "ssrf" {
  bucket        = "ssrf-recipe-${random_uuid.ssrf.result}"
  force_destroy = true
  tags = {
    Name        = "ssrf-recipe-${random_uuid.ssrf.result}"
    Description = "Super Secret Recipe for Frangipane Bucket"
  }
}

resource "aws_s3_object" "secret_ingredient" {
  bucket = aws_s3_bucket.ssrf.id
  key    = "secret_ingredient.txt"
  source = "../files/secret_ingredient.txt"
}

resource "aws_s3_object" "public_recipe" {
  bucket = aws_s3_bucket.ssrf.id
  key    = "public_recipe.txt"
  source = "../files/public_recipe.txt"
}

resource "aws_s3_bucket_acl" "secret-s3-bucket-acl" {
  bucket = aws_s3_bucket.ssrf.id
  acl    = "private"
}
