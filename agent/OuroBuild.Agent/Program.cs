using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace OuroBuild.Agent;

public static class Program
{
    public static void Main(string[] args)
    {
        HostApplicationBuilder builder = Host.CreateApplicationBuilder(args);

        builder.Services.AddWindowsService(options =>
        {
            options.ServiceName = "OuroBuild Agent";
        });

        builder.Services.AddHostedService<Worker>();

        IHost host = builder.Build();

        host.Run();
    }
}