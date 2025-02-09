import { ConversationMessage } from "../types";

export abstract class ChatStorage {

  public isConsecutiveMessage(conversation: ConversationMessage[], newMessage: ConversationMessage): boolean {
    if (conversation.length === 0) return false;
    const lastMessage = conversation[conversation.length - 1];
    return lastMessage.role === newMessage.role;
  }

  protected trimConversation(conversation: ConversationMessage[], maxHistorySize?: number): ConversationMessage[] {
    if (maxHistorySize === undefined) return conversation;
    
    // Ensure maxHistorySize is even to maintain complete binoms
    const adjustedMaxHistorySize = maxHistorySize % 2 === 0 ? maxHistorySize : maxHistorySize - 1;
    
    return conversation.slice(-adjustedMaxHistorySize);
  }

  abstract saveChatMessage(
    userId: string,
    sessionId: string,
    agentId: string,
    newMessage: ConversationMessage,
    maxHistorySize?: number
  ): Promise<ConversationMessage[]>;

  abstract fetchChat(
    userId: string,
    sessionId: string,
    agentId: string,
    maxHistorySize?: number
  ): Promise<ConversationMessage[]>;

  abstract fetchAllChats(
    userId: string,
    sessionId: string
  ): Promise<ConversationMessage[]>;
}