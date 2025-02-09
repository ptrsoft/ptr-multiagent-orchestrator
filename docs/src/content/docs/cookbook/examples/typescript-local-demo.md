---
title: TypeScript Local Demo
description: How to run the Multi-Agent Orchestrator System locally using TypeScript
---

## Prerequisites
- Node.js and npm installed
- AWS account with appropriate permissions
- Basic familiarity with TypeScript and async/await patterns

## Quick Setup

1. Create a new project:
```bash
mkdir test_multi_agent_orchestrator
cd test_multi_agent_orchestrator
npm init
```

2. Install dependencies:
```bash
npm install multi-agent-orchestrator
```

## Implementation

1. Create a new file named `quickstart.ts`:

2. Initialize the orchestrator:
```typescript
import { MultiAgentOrchestrator } from "multi-agent-orchestrator";

const orchestrator = new MultiAgentOrchestrator({
  config: {
    LOG_AGENT_CHAT: true,
    LOG_CLASSIFIER_CHAT: true,
    LOG_CLASSIFIER_RAW_OUTPUT: false,
    LOG_CLASSIFIER_OUTPUT: true,
    LOG_EXECUTION_TIMES: true,
  }
});
```

3. Add specialized agents:
```typescript
import { BedrockLLMAgent } from "multi-agent-orchestrator";

orchestrator.addAgent(
  new BedrockLLMAgent({
    name: "Tech Agent",
    description: "Specializes in technology areas including software development, hardware, AI, cybersecurity, blockchain, cloud computing, emerging tech innovations, and pricing/costs related to technology products and services.",
  })
);

orchestrator.addAgent(
  new BedrockLLMAgent({
    name: "Health Agent",
    description: "Focuses on health and medical topics such as general wellness, nutrition, diseases, treatments, mental health, fitness, healthcare systems, and medical terminology or concepts.",
  })
);
```

4. Implement the main logic:
```typescript
const userId = "quickstart-user";
const sessionId = "quickstart-session";
const query = "What are the latest trends in AI?";
console.log(`\nUser Query: ${query}`);

async function main() {
  try {
    const response = await orchestrator.routeRequest(query, userId, sessionId);
    console.log("\n** RESPONSE ** \n");
    console.log(`> Agent ID: ${response.metadata.agentId}`);
    console.log(`> Agent Name: ${response.metadata.agentName}`);
    console.log(`> User Input: ${response.metadata.userInput}`);
    console.log(`> User ID: ${response.metadata.userId}`);
    console.log(`> Session ID: ${response.metadata.sessionId}`);
    console.log(`> Additional Parameters:`, response.metadata.additionalParams);
    console.log(`\n> Response: ${response.output}`);
  } catch (error) {
    console.error("An error occurred:", error);
  }
}

main();
```

5. Run the application:
```bash
npx ts-node quickstart.ts
```

## Implementation Notes
- Uses default Bedrock Classifier with `anthropic.claude-3-5-sonnet-20240620-v1:0`
- Utilizes Bedrock LLM Agent with `anthropic.claude-3-haiku-20240307-v1:0`
- Implements in-memory storage by default

## Next Steps
- Add additional specialized agents
- Implement persistent storage with DynamoDB
- Add custom error handling
- Implement streaming responses

Ready to build your own multi-agent chat application? Check out the complete [source code](https://github.com/awslabs/multi-agent-orchestrator/tree/main/examples/local-demo) in our GitHub repository.
