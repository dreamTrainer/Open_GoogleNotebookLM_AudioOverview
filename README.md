# Open_GoogleNotebookLM_AudioOverview
this is a simple implementation of audio overview on the notebookLM。
这是一个google notebook音频预览的简单实现

# get started 开始
## 1. use openai api key or any equivalent  api  key 
使用openai 格式api ， 官方和中转都可以 
中转api
https://api.xi-ai.cn/about

## 2. use alibaba tts api  
使用阿里Cosyvoice api
https://help.aliyun.com/zh/dashscope/developer-reference/cosyvoice-api-details?spm=a2c4g.11186623.0.0.6e5723edGCwwmf

 
# 基本原理
- 通过bs爬取公众号文章
- 通过gpt把文章转成两个人对话的数据，格式为json
- 通过阿里api把两个人的每一句话合成语音文件
- 把这些语音文件合成一个文件
