using System.Text.Json.Serialization;

namespace OuroBuild.Agent.Models;

public sealed record AgentHeartbeatRequest(
    [property: JsonPropertyName("version")] string Version);
