const axios = require('axios');
const AWS = require('aws-sdk');

const GUARDIAN_API_KEY = 'YOUR_GUARDIAN_API_KEY';

// Fetch articles from The Guardian API
async function fetchArticles(preferences) {
    const url = `https://content.guardianapis.com/search?api-key=${GUARDIAN_API_KEY}&q=${preferences}&show-fields=body`;
    const response = await axios.get(url);
    const articles = response.data.response.results.map(article => article.fields.body).join(' ');
    return articles;
}

// Summarize text using AWS Comprehend
async function summarizeText(text) {
    const comprehend = new AWS.Comprehend();
    const params = {
        TextList: [text],
        LanguageCode: 'en'
    };
    const result = await comprehend.batchDetectSentiment(params).promise();
    return result.ResultList[0].Sentiment;
}

module.exports = { fetchArticles, summarizeText };