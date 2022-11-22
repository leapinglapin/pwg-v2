Azure needs CORS enabled for head requests for filesaver.js to work:

```
az storage cors clear --services bf --account-name (name) --account-key (key)
az storage cors add --methods HEAD --origins "*" --services bf --account-name (name) --account-key (key)
```

Or through the portal:
https://stackoverflow.com/questions/28894466/how-can-i-set-cors-in-azure-blob-storage-in-portal
