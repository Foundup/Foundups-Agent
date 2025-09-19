// index.js
import OpenAI from 'openai';
import dotenv from 'dotenv';

// Load your .env file
dotenv.config();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

async function run() {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'user', content: 'Say hello in pirate voice.' }
      ]
    });

    console.log(response.choices[0].message.content);
  } catch (error) {
    console.error('OpenAI API error:', error);
  }
}

run();

