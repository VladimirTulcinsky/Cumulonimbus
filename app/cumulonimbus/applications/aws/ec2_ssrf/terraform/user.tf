resource "aws_iam_user" "attacker" {
  name = "attacker"
  path = "/"
}

resource "aws_iam_access_key" "attacker" {
  user = aws_iam_user.attacker.name
}

resource "aws_iam_user_policy_attachment" "attacker" {
  user       = aws_iam_user.attacker.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}
