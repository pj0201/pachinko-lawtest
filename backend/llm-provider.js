/**
 * LLMProvider - 複数LLM APIに対応した抽象インターフェース
 *
 * 対応プロバイダ:
 * - Groq (無料枠対応)
 * - OpenAI (GPT-3.5/4)
 * - Anthropic Claude
 * - Mistral AI
 * - Ollama (ローカル実行、完全無料)
 */

/**
 * LLMプロバイダの基底クラス
 */
class BaseLLMProvider {
  constructor(config = {}) {
    this.config = config;
    this.model = config.model || this.getDefaultModel();
    this.apiKey = config.apiKey;
    this.baseUrl = config.baseUrl;
  }

  getDefaultModel() {
    throw new Error('getDefaultModel() must be implemented');
  }

  async generateResponse(prompt, options = {}) {
    throw new Error('generateResponse() must be implemented');
  }

  async generateQuestions(context, count = 3, options = {}) {
    const systemPrompt = `You are an expert exam question generator for Japanese gambling machine (遊技機) operation licensing.
Create ${count} multiple-choice questions based on the provided context.
Return a JSON array with format: [{"question": "...", "options": ["A", "B", "C", "D"], "correct": 0, "explanation": "..."}]`;

    try {
      const response = await this.generateResponse(systemPrompt + '\n\nContext:\n' + context, {
        temperature: 0.7,
        ...options
      });

      // JSON解析を試みる
      const jsonMatch = response.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return [];
    } catch (error) {
      console.error('Error generating questions:', error);
      return [];
    }
  }

  async categorizeContent(text, options = {}) {
    const systemPrompt = `You are a document categorization expert for Japanese gambling regulations.
Analyze the provided text and categorize it.
Return JSON: {"category": "...", "subcategory": "...", "relevance": 0.0-1.0, "tags": []}`;

    try {
      const response = await this.generateResponse(systemPrompt + '\n\nText:\n' + text, {
        temperature: 0.5,
        ...options
      });

      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return { category: 'unknown', relevance: 0 };
    } catch (error) {
      console.error('Error categorizing content:', error);
      return { category: 'unknown', relevance: 0 };
    }
  }
}

/**
 * Groq プロバイダ (無料枠: ~10k req/月)
 */
class GroqProvider extends BaseLLMProvider {
  getDefaultModel() {
    return 'mixtral-8x7b-32768'; // 高速モデル
  }

  async generateResponse(prompt, options = {}) {
    const axios = (await import('axios')).default;

    if (!this.apiKey) {
      throw new Error('Groq API key is required');
    }

    try {
      const response = await axios.post('https://api.groq.com/openai/v1/chat/completions', {
        model: this.model,
        messages: [
          { role: 'system', content: 'You are a helpful assistant for Japanese gambling regulation questions.' },
          { role: 'user', content: prompt }
        ],
        temperature: options.temperature || 0.7,
        max_tokens: options.maxTokens || 1024,
      }, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      });

      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('Groq API error:', error.message);
      throw new Error(`Groq API failed: ${error.message}`);
    }
  }
}

/**
 * OpenAI プロバイダ (GPT-3.5/4)
 */
class OpenAIProvider extends BaseLLMProvider {
  getDefaultModel() {
    return 'gpt-3.5-turbo';
  }

  async generateResponse(prompt, options = {}) {
    const axios = (await import('axios')).default;

    if (!this.apiKey) {
      throw new Error('OpenAI API key is required');
    }

    try {
      const response = await axios.post('https://api.openai.com/v1/chat/completions', {
        model: this.model,
        messages: [
          { role: 'system', content: 'You are a helpful assistant for Japanese gambling regulation questions.' },
          { role: 'user', content: prompt }
        ],
        temperature: options.temperature || 0.7,
        max_tokens: options.maxTokens || 1024,
      }, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      });

      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('OpenAI API error:', error.message);
      throw new Error(`OpenAI API failed: ${error.message}`);
    }
  }
}

/**
 * Anthropic Claude プロバイダ
 */
class ClaudeProvider extends BaseLLMProvider {
  getDefaultModel() {
    return 'claude-3-5-sonnet-20241022';
  }

  async generateResponse(prompt, options = {}) {
    const axios = (await import('axios')).default;

    if (!this.apiKey) {
      throw new Error('Claude API key is required');
    }

    try {
      const response = await axios.post('https://api.anthropic.com/v1/messages', {
        model: this.model,
        max_tokens: options.maxTokens || 1024,
        system: 'You are a helpful assistant for Japanese gambling regulation questions.',
        messages: [
          { role: 'user', content: prompt }
        ],
      }, {
        headers: {
          'x-api-key': this.apiKey,
          'Content-Type': 'application/json',
          'anthropic-version': '2023-06-01'
        },
        timeout: 30000
      });

      return response.data.content[0].text;
    } catch (error) {
      console.error('Claude API error:', error.message);
      throw new Error(`Claude API failed: ${error.message}`);
    }
  }
}

/**
 * Mistral AI プロバイダ
 */
class MistralProvider extends BaseLLMProvider {
  getDefaultModel() {
    return 'mistral-small';
  }

  async generateResponse(prompt, options = {}) {
    const axios = (await import('axios')).default;

    if (!this.apiKey) {
      throw new Error('Mistral API key is required');
    }

    try {
      const response = await axios.post('https://api.mistral.ai/v1/chat/completions', {
        model: this.model,
        messages: [
          { role: 'system', content: 'You are a helpful assistant for Japanese gambling regulation questions.' },
          { role: 'user', content: prompt }
        ],
        temperature: options.temperature || 0.7,
        max_tokens: options.maxTokens || 1024,
      }, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      });

      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('Mistral API error:', error.message);
      throw new Error(`Mistral API failed: ${error.message}`);
    }
  }
}

/**
 * Ollama プロバイダ (完全無料、ローカル実行)
 */
class OllamaProvider extends BaseLLMProvider {
  getDefaultModel() {
    return 'mistral'; // 軽量で高速
  }

  async generateResponse(prompt, options = {}) {
    const axios = (await import('axios')).default;

    const baseUrl = this.baseUrl || 'http://localhost:11434';

    try {
      const response = await axios.post(`${baseUrl}/api/generate`, {
        model: this.model,
        prompt: prompt,
        stream: false,
        temperature: options.temperature || 0.7,
      }, {
        timeout: 60000 // Ollamaはローカルなので長めに設定
      });

      return response.data.response;
    } catch (error) {
      console.error('Ollama API error:', error.message);
      throw new Error(`Ollama API failed: ${error.message}`);
    }
  }
}

/**
 * LLM プロバイダファクトリ
 */
class LLMProviderFactory {
  static create(provider, config = {}) {
    const providers = {
      'groq': GroqProvider,
      'openai': OpenAIProvider,
      'claude': ClaudeProvider,
      'mistral': MistralProvider,
      'ollama': OllamaProvider,
    };

    const ProviderClass = providers[provider.toLowerCase()];
    if (!ProviderClass) {
      throw new Error(`Unknown provider: ${provider}. Available: ${Object.keys(providers).join(', ')}`);
    }

    return new ProviderClass(config);
  }

  static createFromEnv(provider = null) {
    const selectedProvider = provider || process.env.LLM_PROVIDER || 'groq';
    const apiKey = process.env[`${selectedProvider.toUpperCase()}_API_KEY`];

    if (selectedProvider !== 'ollama' && !apiKey) {
      console.warn(`Warning: API key for ${selectedProvider} not found in environment`);
    }

    return this.create(selectedProvider, {
      apiKey: apiKey,
      model: process.env[`${selectedProvider.toUpperCase()}_MODEL`],
      baseUrl: process.env[`${selectedProvider.toUpperCase()}_BASE_URL`]
    });
  }
}

export { BaseLLMProvider, GroqProvider, OpenAIProvider, ClaudeProvider, MistralProvider, OllamaProvider, LLMProviderFactory };
