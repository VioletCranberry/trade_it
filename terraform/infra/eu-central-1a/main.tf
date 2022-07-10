module "ec2_instance" {
  source           = "../../modules/instance_generic/"

  instance_user = var.instance_user
  _instance_ami = var._instance_ami
  instance_type = var.instance_type
  instance_zone = var.instance_zone

}
