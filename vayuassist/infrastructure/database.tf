resource "random_password" "db_password" {
  length  = 24
  special = true
}

resource "aws_rds_cluster" "main" {
  cluster_identifier      = "${local.name_prefix}-aurora"
  engine                    = "aurora-postgresql"
  engine_mode               = "provisioned"
  engine_version            = "15.4"
  database_name             = "vayuassist"
  master_username           = "vayuassist_user"
  master_password           = random_password.db_password.result
  db_subnet_group_name      = aws_db_subnet_group.main.name
  vpc_security_group_ids    = [aws_security_group.rds.id]
  storage_encrypted         = true
  backup_retention_period   = var.db_backup_retention_days
  skip_final_snapshot       = var.environment == "dev"
  final_snapshot_identifier = var.environment == "prod" ? "${local.name_prefix}-final" : null
  deletion_protection       = var.environment == "prod"
}

resource "aws_rds_cluster_instance" "main" {
  count = var.db_multi_az ? 2 : 1

  identifier         = "${local.name_prefix}-aurora-${count.index + 1}"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = var.db_instance_class
  engine             = aws_rds_cluster.main.engine
  engine_version     = aws_rds_cluster.main.engine_version
}

resource "aws_secretsmanager_secret" "database" {
  name = "vayuassist/database"
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    host          = aws_rds_cluster.main.endpoint
    port          = 5432
    username      = aws_rds_cluster.main.master_username
    password      = random_password.db_password.result
    database      = aws_rds_cluster.main.database_name
    database_url  = "postgresql://${aws_rds_cluster.main.master_username}:${random_password.db_password.result}@${aws_rds_cluster.main.endpoint}:5432/${aws_rds_cluster.main.database_name}"
  })
}
