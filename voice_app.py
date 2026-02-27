import streamlit as st
from openai import OpenAI
import tempfile
import os
from datetime import datetime
import json

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Voice Answering System",
    page_icon="📞",
    layout="wide"
)

# ==================== SESSION STATE ====================
if 'call_history' not in st.session_state:
    st.session_state.call_history = []

if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

if 'business_name' not in st.session_state:
    st.session_state.business_name = 'My Business'

if 'business_hours' not in st.session_state:
    st.session_state.business_hours = '9 AM - 9 PM, Monday to Saturday'

if 'phone_number' not in st.session_state:
    st.session_state.phone_number = '+1234567890'

# ==================== CSS ====================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    #MainMenu, footer {
        visibility: hidden;
    }
    
    .main-header {
        text-align: center;
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 2rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .sub-header {
        text-align: center;
        color: white;
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    .card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        margin: 1rem 0;
    }
    
    .api-box {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    
    .call-record {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #4caf50;
    }
    
    .phone-display {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        text-align: center;
        padding: 1rem;
        background: #f0f2f6;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .status-box {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    .status-active {
        background: #d4edda;
        color: #155724;
        border: 2px solid #28a745;
    }
    
    .status-inactive {
        background: #f8d7da;
        color: #721c24;
        border: 2px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown('<h1 class="main-header">📞 AI Voice Answering System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional AI-Powered Phone Assistant</p>', unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## ⚙️ System Settings")
    
    st.markdown("---")
    
    # Business Settings
    st.markdown("### 🏢 Business Info")
    
    business_name = st.text_input(
        "Business Name",
        value=st.session_state.business_name,
        placeholder="Enter your business name"
    )
    if business_name != st.session_state.business_name:
        st.session_state.business_name = business_name
    
    phone_number = st.text_input(
        "Phone Number",
        value=st.session_state.phone_number,
        placeholder="+1234567890"
    )
    if phone_number != st.session_state.phone_number:
        st.session_state.phone_number = phone_number
    
    business_hours = st.text_area(
        "Business Hours",
        value=st.session_state.business_hours,
        height=100
    )
    if business_hours != st.session_state.business_hours:
        st.session_state.business_hours = business_hours
    
    st.markdown("---")
    
    # API Key
    st.markdown("### 🔑 OpenAI API Key")
    
    api_key = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-..."
    )
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
    
    if st.session_state.api_key:
        st.success("✅ API Key Set")
    else:
        st.warning("⚠️ Enter API Key")
    
    st.markdown("[Get API Key →](https://platform.openai.com/api-keys)")
    
    st.markdown("---")
    
    # Voice Settings
    st.markdown("### 🎙️ Voice Settings")
    
    voice_options = {
        'Alloy (Neutral)': 'alloy',
        'Echo (Deep Male)': 'echo',
        'Fable (British)': 'fable',
        'Onyx (Strong Male)': 'onyx',
        'Nova (Warm Female)': 'nova',
        'Shimmer (Soft Female)': 'shimmer'
    }
    
    selected_voice = st.selectbox(
        "AI Voice",
        options=list(voice_options.keys()),
        index=4
    )
    
    ai_voice = voice_options[selected_voice]
    
    st.markdown("---")
    
    # Stats
    st.markdown("### 📊 Statistics")
    st.metric("Total Calls", len(st.session_state.call_history))
    
    st.markdown("---")
    
    # Clear History
    if st.button("🗑️ Clear Call History", use_container_width=True):
        st.session_state.call_history = []
        st.success("Cleared!")
        st.rerun()

# ==================== MAIN CONTENT ====================

# System Status
col_status1, col_status2 = st.columns(2)

with col_status1:
    if st.session_state.api_key:
        st.markdown('<div class="status-box status-active">🟢 System Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box status-inactive">🔴 System Inactive - Need API Key</div>', unsafe_allow_html=True)

with col_status2:
    st.markdown(f'<div class="phone-display">📞 {st.session_state.phone_number}</div>', unsafe_allow_html=True)

st.markdown("---")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📞 Voice Calls",
    "📋 Call History",
    "📖 Instructions",
    "⚙️ Advanced Settings"
])

# ==================== TAB 1: VOICE CALLS ====================
with tab1:
    st.markdown("## 📞 AI Voice Call System")
    
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your OpenAI API Key in the sidebar to activate the system")
        
        st.markdown("""
        ### 🔑 How to get API Key:
        1. Go to [OpenAI Platform](https://platform.openai.com/signup)
        2. Sign up or log in
        3. Navigate to [API Keys](https://platform.openai.com/api-keys)
        4. Click **"Create new secret key"**
        5. Copy the key and paste in sidebar
        6. Add billing: [Billing](https://platform.openai.com/account/billing)
        """)
    
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎤 Incoming Call Simulation")
            
            st.info("""
            **📞 How This Works:**
            1. Customer records their voice message
            2. Upload the audio file below
            3. AI listens and understands the query
            4. AI generates a voice response
            5. Response is played back automatically
            
            **Perfect for:**
            - Customer inquiries
            - Business hours questions
            - Service information
            - General support
            """)
            
            st.markdown("---")
            
            # Audio Upload
            st.markdown("#### 🎙️ Upload Customer Voice Message")
            
            audio_file = st.file_uploader(
                "Choose audio file (MP3, WAV, M4A, WebM, OGG)",
                type=['mp3', 'wav', 'm4a', 'webm', 'ogg'],
                help="Upload a voice recording from the customer"
            )
            
            if audio_file:
                st.success(f"✅ Audio file uploaded: {audio_file.name}")
                
                # Play uploaded audio
                st.markdown("**📥 Customer's Voice Message:**")
                st.audio(audio_file, format=f'audio/{audio_file.type.split("/")[-1]}')
                
                st.markdown("---")
                
                # Process Button
                if st.button("📞 Process Call & Generate AI Response", type="primary", use_container_width=True):
                    
                    with st.spinner("🎧 AI is listening to the customer..."):
                        try:
                            client = OpenAI(api_key=st.session_state.api_key)
                            
                            # Save temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_file.name.split(".")[-1]}') as tmp:
                                tmp.write(audio_file.read())
                                tmp_path = tmp.name
                            
                            # Speech-to-Text
                            with open(tmp_path, 'rb') as audio:
                                transcript = client.audio.transcriptions.create(
                                    model="whisper-1",
                                    file=audio,
                                    response_format="text"
                                )
                            
                            customer_message = transcript if isinstance(transcript, str) else transcript.text
                            
                            os.unlink(tmp_path)
                            
                            # Display what customer said
                            st.markdown("### 📝 Customer Message (Transcribed):")
                            st.success(f"**Customer said:** {customer_message}")
                            
                            st.markdown("---")
                            
                            # Generate AI Response
                            with st.spinner("🤖 AI is generating response..."):
                                
                                system_prompt = f"""You are a professional phone answering assistant for {st.session_state.business_name}.

Phone Number: {st.session_state.phone_number}
Business Hours: {st.session_state.business_hours}

Your role:
- Answer customer questions professionally
- Provide business information clearly
- Be friendly and helpful
- Keep responses concise (under 100 words)
- If asked about hours, services, location, or contact - provide the information
- If you don't know something, politely say you'll have someone call them back

Always:
- Greet the customer warmly
- Speak naturally as if on a phone call
- End with a friendly closing
- Mention the phone number if they need to call back

Example response style:
"Hello! Thank you for calling {st.session_state.business_name}. [Answer their question]. Is there anything else I can help you with today? Feel free to call us at {st.session_state.phone_number}. Have a great day!"
"""
                                
                                messages = [
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": customer_message}
                                ]
                                
                                response = client.chat.completions.create(
                                    model="gpt-4o",
                                    messages=messages,
                                    temperature=0.7,
                                    max_tokens=300
                                )
                                
                                ai_response = response.choices[0].message.content
                                
                                # Display AI Response
                                st.markdown("### 🤖 AI Response (Text):")
                                st.info(ai_response)
                                
                                st.markdown("---")
                            
                            # Text-to-Speech
                            with st.spinner("🔊 Converting to voice..."):
                                
                                speech = client.audio.speech.create(
                                    model="tts-1",
                                    voice=ai_voice,
                                    input=ai_response,
                                    speed=1.0
                                )
                                
                                # Save audio
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as audio_tmp:
                                    speech.stream_to_file(audio_tmp.name)
                                    audio_response_path = audio_tmp.name
                                
                                # Play AI Voice Response
                                st.markdown("### 🔊 AI Voice Response:")
                                
                                with open(audio_response_path, 'rb') as audio_play:
                                    st.audio(audio_play, format='audio/mp3', autoplay=True)
                                
                                # Download option
                                with open(audio_response_path, 'rb') as audio_download:
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    st.download_button(
                                        "📥 Download AI Response (MP3)",
                                        audio_download,
                                        file_name=f"ai_response_{timestamp}.mp3",
                                        mime="audio/mp3",
                                        use_container_width=True
                                    )
                                
                                # Save to call history
                                call_record = {
                                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'customer_message': customer_message,
                                    'ai_response': ai_response,
                                    'duration': 'N/A'
                                }
                                
                                st.session_state.call_history.insert(0, call_record)
                                
                                # Clean up
                                os.unlink(audio_response_path)
                                
                                st.success("✅ Call processed successfully!")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            st.info("Please check your API key and ensure you have credits available.")
            
            else:
                st.info("👆 Upload an audio file to simulate an incoming call")
        
        with col2:
            st.markdown("### 📱 Recording Guide")
            
            st.markdown("""
            **Mobile Apps:**
            
            📱 **iPhone:**
            - Voice Memos (built-in)
            - Just Record
            
            📱 **Android:**
            - Voice Recorder
            - Easy Voice Recorder
            
            **Desktop:**
            
            💻 **Windows:**
            - Voice Recorder (built-in)
            - Audacity (free)
            
            💻 **Mac:**
            - QuickTime Player
            - Voice Memos
            
            🌐 **Online (No App):**
            - [vocaroo.com](https://vocaroo.com)
            - [online-voice-recorder.com](https://online-voice-recorder.com)
            """)
            
            st.markdown("---")
            
            st.markdown("### 💡 Tips")
            
            st.info("""
            **For Best Results:**
            - Record in a quiet place
            - Speak clearly
            - Keep messages under 1 minute
            - Save as MP3 or WAV
            
            **Test Questions:**
            - "What are your business hours?"
            - "How can I contact you?"
            - "What services do you offer?"
            - "Are you open on weekends?"
            """)
            
            st.markdown("---")
            
            st.markdown("### 🎙️ Current Voice")
            st.success(f"**Using:** {selected_voice}")
            
            # Test voice
            if st.button("🔊 Test Voice", use_container_width=True):
                try:
                    client = OpenAI(api_key=st.session_state.api_key)
                    
                    test_text = f"Hello! Thank you for calling {st.session_state.business_name}. How may I help you today?"
                    
                    with st.spinner("Generating..."):
                        speech = client.audio.speech.create(
                            model="tts-1",
                            voice=ai_voice,
                            input=test_text
                        )
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                            speech.stream_to_file(tmp.name)
                            with open(tmp.name, 'rb') as audio:
                                st.audio(audio, format='audio/mp3')
                            os.unlink(tmp.name)
                except:
                    st.error("Could not generate test")

# ==================== TAB 2: CALL HISTORY ====================
with tab2:
    st.markdown("## 📋 Call History")
    
    if st.session_state.call_history:
        st.info(f"📞 Total Calls: {len(st.session_state.call_history)}")
        
        st.markdown("---")
        
        for i, call in enumerate(st.session_state.call_history):
            with st.expander(f"📞 Call #{len(st.session_state.call_history) - i} - {call['timestamp']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🎤 Customer Message:**")
                    st.write(call['customer_message'])
                
                with col2:
                    st.markdown("**🤖 AI Response:**")
                    st.write(call['ai_response'])
                
                st.markdown(f"**⏱️ Time:** {call['timestamp']}")
        
        st.markdown("---")
        
        # Export History
        if st.button("📥 Export Call History (JSON)", use_container_width=True):
            history_json = json.dumps(st.session_state.call_history, indent=2)
            st.download_button(
                "Download JSON",
                history_json,
                file_name=f"call_history_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    else:
        st.info("📭 No calls yet. Process a call in the Voice Calls tab to see history here.")

# ==================== TAB 3: INSTRUCTIONS ====================
with tab3:
    st.markdown("## 📖 How to Use This System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 Quick Start
        
        **Step 1: Setup (One Time)**
        1. Enter your business name in sidebar
        2. Enter your phone number
        3. Set your business hours
        4. Add OpenAI API Key
        5. Choose AI voice
        
        **Step 2: Test the System**
        1. Record a test message on your phone
        2. Ask something like "What are your hours?"
        3. Upload the audio file
        4. Click "Process Call"
        5. Listen to AI response
        
        **Step 3: Go Live**
        - System is ready to handle real calls
        - Upload any customer voice message
        - AI responds automatically
        - Download responses if needed
        """)
    
    with col2:
        st.markdown("""
        ### 💡 Use Cases
        
        **Perfect For:**
        - Customer service calls
        - After-hours support
        - FAQ answering
        - Business information
        - Basic inquiries
        - Appointment info
        
        **What AI Can Handle:**
        - Business hours questions
        - Location/contact info
        - Service descriptions
        - Pricing inquiries
        - General support
        - Callback requests
        
        **Limitations:**
        - Cannot make real-time calls yet
        - Upload/response workflow
        - Requires internet
        - Needs API credits
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🔗 Integration Options (Future)
    
    **Coming Soon:**
    - Direct phone number integration via Twilio
    - Real-time call handling
    - Automatic call recording
    - SMS notifications
    - Call analytics dashboard
    - Multi-language support
    """)

# ==================== TAB 4: ADVANCED SETTINGS ====================
with tab4:
    st.markdown("## ⚙️ Advanced Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 AI Behavior")
        
        response_style = st.selectbox(
            "Response Style",
            ["Professional", "Friendly", "Casual", "Formal"]
        )
        
        response_length = st.select_slider(
            "Response Length",
            options=["Very Short", "Short", "Medium", "Long"],
            value="Medium"
        )
        
        include_callback = st.checkbox("Include callback offer in responses", value=True)
        
        include_hours = st.checkbox("Always mention business hours", value=True)
        
        st.markdown("---")
        
        st.markdown("### 🎙️ Voice Quality")
        
        audio_speed = st.slider(
            "Speech Speed",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        st.info(f"Current speed: {audio_speed}x")
    
    with col2:
        st.markdown("### 📊 System Info")
        
        st.markdown(f"""
        **Business Name:** {st.session_state.business_name}
        
        **Phone Number:** {st.session_state.phone_number}
        
        **Hours:** {st.session_state.business_hours}
        
        **AI Voice:** {selected_voice}
        
        **API Status:** {"✅ Active" if st.session_state.api_key else "❌ Inactive"}
        
        **Total Calls:** {len(st.session_state.call_history)}
        """)
        
        st.markdown("---")
        
        st.markdown("### 💰 API Usage")
        
        st.info("""
        **Estimated Cost per Call:**
        - Speech-to-Text: ~$0.01
        - GPT-4 Response: ~$0.02
        - Text-to-Speech: ~$0.02
        
        **Total: ~$0.05 per call**
        
        $5 credit = ~100 calls
        """)
    
    st.markdown("---")
    
    # Danger Zone
    st.markdown("### ⚠️ Danger Zone")
    
    col_danger1, col_danger2 = st.columns(2)
    
    with col_danger1:
        if st.button("🗑️ Clear All Call History", type="secondary", use_container_width=True):
            st.session_state.call_history = []
            st.success("History cleared!")
            st.rerun()
    
    with col_danger2:
        if st.button("♻️ Reset All Settings", type="secondary", use_container_width=True):
            st.session_state.business_name = 'My Business'
            st.session_state.business_hours = '9 AM - 9 PM, Monday to Saturday'
            st.session_state.phone_number = '+1234567890'
            st.success("Settings reset!")
            st.rerun()

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; opacity: 0.7; padding: 2rem;">
    <p style="color: white; font-size: 0.9rem;">
        📞 AI Voice Answering System | Powered by OpenAI Whisper & GPT-4
    </p>
    <p style="color: white; font-size: 0.8rem;">
        Professional AI Phone Assistant for Your Business
    </p>
</div>
""", unsafe_allow_html=True)
