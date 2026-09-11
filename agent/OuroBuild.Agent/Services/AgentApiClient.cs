using System.Net.Http.Json;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using OuroBuild.Agent.Models;

namespace OuroBuild.Agent.Services;

public sealed class AgentApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<AgentApiClient> _logger;

    public AgentApiClient(
        HttpClient httpClient,
        IConfiguration configuration,
        ILogger<AgentApiClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;

        string baseUrl = configuration[
            "Agent:ApiBaseUrl"] ?? "http://localhost:8000";

        _httpClient.BaseAddress = new Uri(
            baseUrl.TrimEnd('/') + "/");
    }

    public async Task<AgentRegistrationResponse?> RegisterAsync(
        AgentRegistrationRequest request,
        CancellationToken cancellationToken)
    {
        using HttpResponseMessage response =
            await _httpClient.PostAsJsonAsync(
                "agents/register",
                request,
                cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            string body = await response.Content.ReadAsStringAsync(
                cancellationToken);

            _logger.LogError(
                "Registro do Agent falhou. HTTP {StatusCode}. " +
                "Resposta: {Response}",
                (int)response.StatusCode,
                body);

            return null;
        }

        return await response.Content.ReadFromJsonAsync<
            AgentRegistrationResponse>(
                cancellationToken: cancellationToken);
    }

    public async Task<AgentRegistrationResponse?> HeartbeatAsync(
        int agentId,
        AgentHeartbeatRequest request,
        CancellationToken cancellationToken)
    {
        using HttpResponseMessage response =
            await _httpClient.PostAsJsonAsync(
                $"agents/{agentId}/heartbeat",
                request,
                cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            string body = await response.Content.ReadAsStringAsync(
                cancellationToken);

            _logger.LogError(
                "Heartbeat do Agent falhou. HTTP {StatusCode}. " +
                "Resposta: {Response}",
                (int)response.StatusCode,
                body);

            return null;
        }

        return await response.Content.ReadFromJsonAsync<
            AgentRegistrationResponse>(
                cancellationToken: cancellationToken);
    }
}
