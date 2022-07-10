output "instance_eip" {
  value = aws_eip.instance_generic_ip.public_ip
}

output "instance_dns" {
  value = aws_eip.instance_generic_ip.public_dns
}
