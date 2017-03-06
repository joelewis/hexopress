class Utils {
    static getSearchParams() {
        if (!location.search.trim()) {
            return null
        }
        var search = location.search.substring(1)
        return JSON.parse('{"' + decodeURI(search).replace(/"/g, '\\"').replace(/&/g, '","').replace(/=/g,'":"') + '"}')
    }
    
    static unescapeHTML(escapedStr)  {
        var t = document.createElement('textarea')
        t.innerHTML = escapedStr
        return t.value
    }
}

export default Utils