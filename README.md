# Topic Detection (NLP)  using Azure Functions

This project demos how to use Spacy, NTLK to do topic modeling (NLP) on Azure Functions. 

The API is designed to be compatible with Azure Cognitive Search, so you can use it as a custom skill in Azure Search. 

Right now it works on Azure Functions emulator, we are working to have a version that can be deployed to the cloud. 

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

