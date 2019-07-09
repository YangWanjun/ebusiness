# Database
docker run --name mysql -p 3306:3306 -v /home/ec2-user/mysql_data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=root -d mysql:5.6.41 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci --innodb_use_native_aio=0
# Server
docker run -d --name ebusiness --link mysql:mysql -v /home/ec2-user/ebusiness_files:/eb_sales_files -v /home/ec2-user/ebusiness:/ebusiness yangwanjun/sales-ubuntu:env python /ebusiness/manage.py runserver 0.0.0.0:80
# nignx
docker run -d --restart=always --name nginx -p 80:80 -p 443:443  --link ebusiness:ebusiness -v /home/ec2-user/nginx/default.conf:/etc/nginx/conf.d/default.conf -v /home/ec2-user/ssl/.lego/certificates:/certificates nginx:alpine
# ＳＳＬ証明書
docker run --rm -p 80:80 -v /home/ec2-user/ssl/.lego:/.lego  xenolf/lego --email="ywjsailor@gmail.com" --domains="service.area-parking.com" --accept-tos run
