![](./assets/banner.jpg)

<h1 align="center">Open-Storybook-VTuber</h1>
<h3 align="center">
An offline-ready, voice-interactive storybook companion that brings your favorite characters to life.
</h3>

[![license](https://img.shields.io/github/license/t41372/Open-LLM-VTuber)](https://github.com/t41372/Open-LLM-VTuber/blob/master/LICENSE)
[![Discord](https://img.shields.io/badge/Discord-Join%20our%20storybook%20server-5865F2?logo=discord&logoColor=white)](https://discord.gg/storybook-vtuber)

English README

> ⚠️ This project is a fork of Open-LLM-VTuber, refocused on **interactive storybook characters** instead of general AI companions.


## ⭐️ What is this project?

**Open-Storybook-VTuber**는 실시간 음성 기반으로 **동화책 속 캐릭터와 대화할 수 있는 애플리케이션**입니다.  
일반적인 AI 비서와 대화하는 대신, 사용자는 **동화 속 해설자, 주인공, 혹은 안내자 역할을 하는 캐릭터와 직접 이야기**하게 됩니다.

이 앱은 로컬 환경에서 실행되며, **Live2D 아바타**, **자동 음성 인식(ASR)**, **텍스트 음성 변환(TTS)** 를 이용해 캐릭터를 실제로 살아 있는 것처럼 느끼게 합니다.  
사용자는 이야기를 함께 읽고, 줄거리에 대해 질문하고, 등장인물의 감정이나 교훈에 대해 물어보면서 **인터랙티브 스토리텔링**을 경험할 수 있습니다.

**어린이와 부모가 함께 사용할 수 있는, 가족 친화적인 동화 중심 경험**에 초점을 맞추었습니다.


## ✨ Features & Highlights

- 📚 **Story-focused interaction**  
  일반적인 챗봇이 아니라 **동화책 속 캐릭터와 직접 대화**합니다.  
  줄거리, 등장인물, 이야기의 교훈에 대해 자연스럽게 질문하고 답을 들을 수 있습니다.

- 🎤 **Real-time voice conversation**  
  마이크로 말을 걸면, 낮은 지연 시간의 ASR/LLM/TTS 파이프라인을 통해 **거의 실시간에 가까운 음성 응답**을 받습니다.

- 🧸 **Live2D storybook avatar**  
  Live2D 캐릭터가 표정과 동작으로 반응하여, 마치 동화 속 인물이 화면 밖으로 나온 것 같은 느낌을 줍니다.

- 🔒 **Offline-friendly by design**  
  Ollama, llama.cpp 등 **로컬 LLM/ASR/TTS 백엔드**를 사용할 수 있도록 설계되어,  
  인터넷 연결 없이도 동작하며, 대화 내용이 외부 서버로 전송되지 않도록 구성할 수 있습니다.

- 🛠️ **Configurable but focused**  
  YAML 설정 파일을 통해 **동화 제목, 기본 캐릭터 페르소나, 언어 설정** 등을 쉽게 바꿀 수 있습니다.  
  기본 설정은 “안전하고 동화 중심인 경험”에 맞춰져 있으며, 필요할 때만 고급 기능을 켜도록 설계하는 것을 목표로 합니다.


## 🚀 Quick Start

설치 및 실행 방법은 원 프로젝트(Open-LLM-VTuber)의 설치 방식과 거의 동일합니다.  
아래는 대표적인 로컬 실행 예시입니다.

1. Python 3.10+ 및 `uv` 환경을 준비합니다.  
2. 프로젝트 디렉터리로 이동한 뒤 의존성을 설치합니다.  
   - `uv sync`  
3. 서버를 실행합니다.  
   - `uv run python run_server.py`  
4. 브라우저에서 서버가 띄워주는 URL(예: `http://localhost:12393`)에 접속하면,  
   동화 캐릭터와 대화할 수 있는 웹 클라이언트를 사용할 수 있습니다.

로컬 LLM/ASR/TTS 설정은 `conf.yaml` 및 `config_templates` 아래 템플릿 파일을 참고하여 조정할 수 있습니다.


## 😢 Uninstall

대부분의 파일(파이썬 의존성, 모델 파일 등)은 이 프로젝트 폴더 내부에 저장됩니다.  
프로젝트 디렉터리를 삭제하면 대부분의 관련 파일이 함께 삭제됩니다.

다만 ModelScope 또는 Hugging Face를 통해 내려받은 모델은 `MODELSCOPE_CACHE`, `HF_HOME` 등의 별도 캐시 디렉터리에 있을 수 있습니다.  
용량을 완전히 정리하고 싶다면, 해당 캐시 디렉터리도 함께 확인해 주세요.

또한 설치 과정에서 별도로 설치한 도구들(`uv`, `ffmpeg`, `deeplx` 등)이 더 이상 필요 없다면 각 도구의 가이드를 참고하여 제거할 수 있습니다.


## 📜 Third-Party Licenses

### Live2D Sample Models Notice

이 프로젝트에는 Live2D Inc.에서 제공하는 Live2D 샘플 모델이 포함되어 있습니다.  
이 에셋들은 이 리포지토리의 MIT 라이선스와는 별도로, **Live2D Free Material License Agreement** 및  
**Live2D Cubism Sample Data 이용 약관**의 적용을 받습니다.

해당 샘플 데이터는 Live2D Inc.가 소유한 저작물이며, 위 약관에 따라 사용됩니다.  
자세한 내용은 다음 링크를 참고하세요:
- [Live2D Free Material License Agreement](https://www.live2d.jp/en/terms/live2d-free-material-license-agreement/)
- [Terms of Use](https://www.live2d.com/eula/live2d-sample-model-terms_en.html)

특히 **상업적 이용**, 또는 **중·대규모 기업**에서의 활용을 계획하고 있다면,  
이 샘플 모델을 사용하는 데 추가 라이선스가 필요할 수 있습니다.  
이 프로젝트를 상업적으로 사용하려면 Live2D Inc.로부터 적절한 권한을 받거나,  
해당 샘플 모델이 제거된 별도 버전을 사용하는 것을 권장합니다.


## Contributors

이 프로젝트와 원 프로젝트(Open-LLM-VTuber)를 함께 발전시켜 준 모든 기여자분들께 감사드립니다.

<a href="https://github.com/Open-LLM-VTuber/Open-LLM-VTuber/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Open-LLM-VTuber/Open-LLM-VTuber" />
</a>