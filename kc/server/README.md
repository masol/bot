[![forthebadge](https://www.prodvest.com/img/logodd.png)](http://www.prodvest.com)

*由BOT创建的代码*

<h1>目录</h1>

- [使用说明](#使用说明)

# 使用说明
&emsp;&emsp;安装docker。确保docker中旧镜像不存在．可以执行如下命令清空docker内容:
```bash
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls -q)
#docker rmi $(docker images -a -q)
```
