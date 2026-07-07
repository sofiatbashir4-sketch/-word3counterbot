"""
Word3CounterBot - A Telegram bot for text analysis
Deployed on Railway with GitHub integration
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Tuple

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Flask for Railway health checks
from flask import Flask, jsonify
import threading

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================
# FLASK APP FOR RAILWAY HEALTH CHECKS
# ============================================================

flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'bot': '@word3counterbot',
        'timestamp': datetime.now().isoformat()
    })

@flask_app.route('/health')
def health():
    """Simple health check"""
    return 'OK', 200

# ============================================================
# BOT CONFIGURATION
# ============================================================

BOT_USERNAME = "word3counterbot"
BOT_NAME = "Word3 Counter Bot"
VERSION = "1.0.0"

# Common stop words
STOP_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
    'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
    'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
    'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
    'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your',
    'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
    'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
    'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
    'give', 'day', 'most', 'us'
}

# ============================================================
# TEXT ANALYSIS FUNCTIONS
# ============================================================

class TextAnalyzer:
    """Comprehensive text analysis engine"""
    
    @staticmethod
    def analyze_text(text: str) -> Dict:
        """Analyze text and return all statistics"""
        if not text or len(text.strip()) < 1:
            return {'error': 'Empty text'}
        
        clean_text = text.strip()
        
        # Count words
        words = re.findall(r'\b\w+\b', clean_text)
        word_count = len(words)
        
        # Count characters
        char_with_spaces = len(clean_text)
        char_without_spaces = len(clean_text.replace(' ', ''))
        
        # Count sentences
        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        # Count paragraphs
        paragraphs = [p for p in clean_text.split('\n') if p.strip()]
        paragraph_count = len(paragraphs) if paragraphs else 1
        
        # Word statistics
        if words:
            avg_word_length = sum(len(w) for w in words) / len(words)
            longest_word = max(words, key=len)
            shortest_word = min(words, key=len)
        else:
            avg_word_length = 0
            longest_word = 'N/A'
            shortest_word = 'N/A'
        
        # Reading time (200 words per minute)
        if word_count < 50:
            reading_time = f"{10} sec"
        else:
            minutes = max(0.5, word_count / 200)
            seconds = int(minutes * 60)
            reading_time = f"{minutes:.1f} min ({seconds} sec)"
        
        # Keywords
        keyword_stats = {}
        if words:
            word_freq = {}
            for w in words:
                w_lower = w.lower()
                if w_lower not in STOP_WORDS and len(w_lower) > 2:
                    word_freq[w_lower] = word_freq.get(w_lower, 0) + 1
            
            sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            for word, count in sorted_keywords:
                percentage = (count / word_count) * 100
                keyword_stats[word] = {
                    'count': count,
                    'percentage': round(percentage, 1)
                }
        
        return {
            'word_count': word_count,
            'characters_with_spaces': char_with_spaces,
            'characters_without_spaces': char_without_spaces,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'avg_word_length': round(avg_word_length, 2),
            'longest_word': longest_word,
            'shortest_word': shortest_word,
            'reading_time': reading_time,
            'keywords': keyword_stats,
            'has_content': word_count > 0
        }

# ============================================================
# BOT HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    first_name = user.first_name if user else 'User'
    
    welcome_text = f"""
👋 *Hello {first_name}!*

Welcome to *{BOT_NAME}*! 🎯

Send me any text and I'll analyze it instantly!

*📊 What I can analyze:*
• 📝 Word count
• 🔤 Characters (with/without spaces)
• 📄 Sentences & paragraphs
• ⏱️ Reading time
• 📐 Average word length
• 🔑 Keyword density

*🚀 Quick Start:*
Just send me any text message!

*📚 Commands:*
/start - Show this message
/help - Detailed help
/about - Bot information

Ready to analyze! 🎉
"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = f"""
📚 *Help Center - {BOT_NAME}*

*🤖 How to Use:*
Simply send any text message and I'll analyze it!

*📝 Commands:*
/start - Start the bot
/help - Show this help
/about - About this bot

*📊 Analysis Includes:*
• Total word count
• Characters (with & without spaces)
• Number of sentences
• Number of paragraphs
• Average word length
• Longest & shortest words
• Estimated reading time
• Top 5 keywords

*💡 Tips:*
• Send longer texts for better analysis
• Send /about to learn more about this bot

Need help? Just ask! 🤝
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = f"""
🤖 *About {BOT_NAME}*

*Version:* {VERSION}
*Platform:* Telegram Bot API
*Hosting:* Railway + GitHub
*Language:* Python 3.10+

*✨ Features:*
• Real-time text analysis
• Accurate word counting
• Character analysis
• Sentence & paragraph detection
• Reading time estimation
• Keyword extraction
• 100% free to use
• No registration required

*🛠️ Technologies:*
• python-telegram-bot
• Flask for webhooks
• Railway for hosting
• GitHub for version control

Made with ❤️ for the community
"""
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    text = update.message.text
    
    if text.startswith('/'):
        return
    
    if len(text.strip()) < 3:
        await update.message.reply_text(
            "⚠️ Please send a longer text (at least 3 characters)!"
        )
        return
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    # Analyze
    analysis = TextAnalyzer.analyze_text(text)
    
    if 'error' in analysis:
        await update.message.reply_text("⚠️ Error analyzing text. Please try again.")
        return
    
    # Build response
    response = f"""
📊 *Text Analysis Results*

📝 *Words:* {analysis['word_count']}
🔤 *Characters (with spaces):* {analysis['characters_with_spaces']}
📏 *Characters (without spaces):* {analysis['characters_without_spaces']}
📄 *Sentences:* {analysis['sentence_count']}
📑 *Paragraphs:* {analysis['paragraph_count']}

*📐 Word Statistics:*
• Average length: {analysis['avg_word_length']} characters
• Longest: `{analysis['longest_word']}`
• Shortest: `{analysis['shortest_word']}`

⏱️ *Reading Time:* {analysis['reading_time']}
"""
    
    # Add keywords if available
    if analysis['keywords']:
        response += "\n*🔑 Top Keywords:*\n"
        for word, data in analysis['keywords'].items():
            response += f"• `{word}`: {data['count']} times ({data['percentage']}%)\n"
    
    # Add inline buttons
    keyboard = [
        [
            InlineKeyboardButton("🔄 Analyze More", callback_data="more"),
            InlineKeyboardButton("📊 Stats", callback_data="stats")
        ],
        [
            InlineKeyboardButton("📝 Examples", callback_data="examples"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        response,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "more":
        await query.edit_message_text(
            "📝 *Send me your text for analysis!*\n\n"
            "I'll analyze words, characters, sentences, and more.",
            parse_mode='Markdown'
        )
    elif query.data == "stats":
        await query.edit_message_text(
            "📊 *Statistics*\n\n"
            "Send me any text for detailed analysis!\n"
            "I'll show you word count, character count, reading time, and more.",
            parse_mode='Markdown'
        )
    elif query.data == "examples":
        examples = """
📝 *Example Texts to Analyze*

*Short:*
"The quick brown fox jumps over the lazy dog."

*Medium:*
"Artificial intelligence is transforming our world. From healthcare to transportation, AI is making tasks more efficient. However, we must consider the ethical implications."

*Long:*
"Technology has revolutionized the way we live, work, and communicate. Smartphones have become essential. The internet connects billions of people globally. Social media allows instant sharing. While these developments bring benefits, they also present challenges."
"""
        await query.edit_message_text(examples, parse_mode='Markdown')
    elif query.data == "help":
        await help_command(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Sorry, an error occurred. Please try again."
            )
        except:
            pass

# ============================================================
# MAIN FUNCTION
# ============================================================

def run_bot():
    """Start the bot"""
    token = os.environ.get('BOT_TOKEN')
    
    if not token:
        logger.error("❌ BOT_TOKEN environment variable not set!")
        return
    
    try:
        logger.info(f"🤖 Starting {BOT_NAME}...")
        application = Application.builder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_error_handler(error_handler)
        
        # Start
        logger.info("🚀 Bot is running...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == '__main__':
    # Start Flask in background for Railway health checks
    def run_flask():
        port = int(os.environ.get('PORT', 8080))
        flask_app.run(host='0.0.0.0', port=port, debug=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Run the bot
    run_bot()
