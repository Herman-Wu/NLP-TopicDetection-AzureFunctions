# Topic Detection (NLP)  using Azure Functions

This project demos how to use Spacy, NTLK to do topic modeling (NLP) on Azure Functions. 

The API is designed to be compatible with Azure Cognitive Search, so you can use it as a custom skill in Azure Search. 

Right now it works on Azure Functions emulator, we are working to have a version that can be deployed to the cloud. 

[Update] It also works when deployed to Azure Functions. But you need to download/copy en_core_web_sm (it is normally located in your python environment site-packages\en_core_web_sm folder. For example in  my enronment it's in Anaconda3\Lib\site-packages\en_core_web_sm folder) first and put it in project folder or save it in Azure blob storage and [mount the storage to Azure functions](https://github.com/Azure/Azure-Functions/wiki/Bring-your-own-storage-(Linux-consumption)).   

After running the functions in Azure Functions emulator, you can test it by post the following JSON message to the service. 


```json
{
  "values": [
    {
      "recordId": "id1",
      "data": {
        "text": "But it is not clear if the stark message is getting through to everybody, especially younger Americans, who are vital to stopping a disease now spreading like wildfire before it reaches levels that could overwhelm the US health system."
      }
    },
    {
      "recordId": "id2",
      "data": {
        "text": "While there were new signs that the White House was gearing up its mitigation program -- in terms of testing, economic repair work and calls for industry to donate masks to health care workers -- the effort still seemed short of what was needed."
      }
    },
    {
      "recordId": "id3",
      "data": {
        "text": "The State Department is working to verify the information coming in, crosschecking the tips where possible with other sources, such as human rights organizations, and checking to see if a high number of tips say the same thing, the official said."
      }
    }
  ]
}

```

**Note:**

You will need to set data path (the path points to en_core_web_sm ) for Spacy in Azure Functions.  

```python
spacy.util.set_data_path(rootfolder)
```
Otherwise you will get error like following 

```json
{
    "error": "[E050] Can't find model 'en_core_web_sm'. It doesn't seem to be a shortcut link, a Python package or a valid path to a data directory."
}
```

#### Reference
[SpaCy model won't load in AWS Lambda](https://stackoverflow.com/questions/47879258/spacy-model-wont-load-in-aws-lambda)

[Bring your own storage (Linux consumption)](https://github.com/Azure/Azure-Functions/wiki/Bring-your-own-storage-(Linux-consumption))