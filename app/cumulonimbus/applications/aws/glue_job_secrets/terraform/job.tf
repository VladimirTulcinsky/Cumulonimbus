resource "random_id" "suffix" {
  byte_length = 4
}

# S3 bucket for the Glue script — contents are irrelevant to the challenge
resource "aws_s3_bucket" "scripts" {
  bucket        = "cumulonimbus-glue-${random_id.suffix.hex}"
  force_destroy = true
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_s3_object" "script" {
  bucket  = aws_s3_bucket.scripts.id
  key     = "scripts/etl_job.py"
  content = <<-PYTHON
    import sys
    from awsglue.context import GlueContext
    from pyspark.context import SparkContext

    sc = SparkContext()
    glueContext = GlueContext(sc)
    print("ETL job starting")
  PYTHON
}

data "aws_iam_policy_document" "glue_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "glue" {
  name               = "cumulonimbus-glue-${random_id.suffix.hex}"
  assume_role_policy = data.aws_iam_policy_document.glue_assume.json
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Glue job with credentials hardcoded in default_arguments — readable via glue:GetJob
resource "aws_glue_job" "etl" {
  name         = "cumulonimbus-etl-${random_id.suffix.hex}"
  role_arn     = aws_iam_role.glue.arn
  glue_version = "4.0"

  command {
    script_location = "s3://${aws_s3_bucket.scripts.bucket}/${aws_s3_object.script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"    = "python"
    "--TempDir"         = "s3://${aws_s3_bucket.scripts.bucket}/tmp/"
    "--database-host"   = "prod-db.internal.example.com"
    "--database-name"   = "appdb"
    "--database-user"   = "etl_svc"
    "--database-password" = "Pr0d_DB_P4ss!"
    "--api-key"         = "CUMULONIMBUS{Glu3_J0b_S3cr3ts_1n_4rgum3nts}"
  }

  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

# Attacker IAM user with glue:GetJob + glue:ListJobs
resource "aws_iam_user" "attacker" {
  name = "glue-reader-${random_id.suffix.hex}"
  tags = {
    app_id  = var.app_id
    managed = "terraform"
  }
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

data "aws_iam_policy_document" "attacker" {
  statement {
    sid    = "GlueRead"
    effect = "Allow"
    actions = [
      "glue:GetJob",
      "glue:ListJobs",
      "glue:GetJobs",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_user_policy" "attacker" {
  name   = "glue-reader-policy-${random_id.suffix.hex}"
  user   = aws_iam_user.attacker.name
  policy = data.aws_iam_policy_document.attacker.json
}
