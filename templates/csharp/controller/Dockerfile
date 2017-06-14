FROM avatao/mono-controller:ubuntu-14.04
MAINTAINER Gergo Turcsanyi <gergo.turcsanyi@avatao.com>

COPY ./controller/ /

RUN cd /home/user/App \
	&& find . -type f -exec chmod 744 {} + \
	&& chown -R controller:controller /home/user/App /nunit \
	&& chown root:root /home/user/App/App/App.csproj /home/user/App/Test/Test.csproj \
	&& chown root:root /home/user/App/App.sln /home/user/App/Test/Test.cs

USER controller

RUN  cp /opt/Solution.cs /home/user/App/App/Program.cs \
	&& xbuild /home/user/App/App.sln

#RUN cd /nunit/bin \
#	&& mono nunit3-console.exe /home/user/App/Test/Test.csproj

VOLUME ["/home/user"]
