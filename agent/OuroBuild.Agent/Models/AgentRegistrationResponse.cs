using System.Text.Json.Serialization;

namespace OuroBuild.Agent.Models;

public sealed record AgentRegistrationResponse(
    [property: JsonPropertyName("id")] int Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("machine_name")] string MachineName,
    [property: JsonPropertyName("user_name")] string UserName,
    [property: JsonPropertyName("version")] string Version,
    [property: JsonPropertyName("status")] string Status);
