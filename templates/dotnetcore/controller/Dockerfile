FROM avatao/netcore-controller:ubuntu-16.04

USER root

COPY ./controller /

RUN cd /home/controller/Program \
	&& find . -type f -exec chmod 744 {} + \
	&& chown -R controller:controller /home/controller 

USER controller

RUN cd /home/controller/Program/Test \
	&& dotnet restore \
	&& dotnet build /home/controller/Program/Program.sln

USER root

RUN chown root:root /home/controller/Program/App/App.csproj \
	&& chown root:root /home/controller/Program/Test/Test.csproj \
	&& chown root:root /home/controller/Program/Program.sln

VOLUME ["/home/controller"]

USER controller
