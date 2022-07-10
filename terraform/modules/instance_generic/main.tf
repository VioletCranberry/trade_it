resource "aws_key_pair" "infra" {
  key_name   = "infra-key"
  public_key = file("${path.module}/files/${var.instance_zone}/ssh_key.pub")
}

resource "aws_instance" "instance_generic" {
  ami               = var._instance_ami
  instance_type     = var.instance_type
  availability_zone = var.instance_zone
  key_name          = aws_key_pair.infra.id
  security_groups   = [
    "${aws_security_group.instance_generic.name}"
  ]
  tags = {
    Name = "instance_generic"
    Role = "instance_generic"
  }
  user_data = <<EOF
    #cloud-config
    system_info:
      default_user:
        name: "${var.instance_user}"
  EOF
}

resource "aws_security_group" "instance_generic" {
  name        = "allow_traffic_flow"
  description = "allow_traffic_flow"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [
      "${data.http.source_ip.body}/32"
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "instance_generic"
    Role = "instance_generic"
  }
}

resource "aws_eip" "instance_generic_ip" {
  instance = aws_instance.instance_generic.id
  vpc      = true

  depends_on = [
    aws_instance.instance_generic
  ]

  tags = {
    Name = "instance_generic"
    Role = "instance_generic"
  }
}
