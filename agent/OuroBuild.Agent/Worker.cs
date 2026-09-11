using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace OuroBuild.Agent;

public sealed class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;

    public Worker(ILogger<Worker> logger)
    {
        _logger = logger;
    }

    protected override async Task ExecuteAsync(
        CancellationToken stoppingToken)
    {
        string machineName = Environment.MachineName;
        string userName = Environment.UserName;
        string domainName = Environment.UserDomainName;

        _logger.LogInformation(
            "OuroBuild Agent iniciado.");

        _logger.LogInformation(
            "Máquina: {MachineName}",
            machineName);

        _logger.LogInformation(
            "Usuário: {DomainName}\\{UserName}",
            domainName,
            userName);

        while (!stoppingToken.IsCancellationRequested)
        {
            _logger.LogInformation(
                "OuroBuild Agent ativo. Aguardando trabalho.");

            await Task.Delay(
                TimeSpan.FromSeconds(10),
                stoppingToken);
        }

        _logger.LogInformation(
            "OuroBuild Agent finalizado.");
    }
}