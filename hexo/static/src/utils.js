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

    static getHost() {
        if (!window.location.origin) {
        window.location.origin = window.location.protocol + "//" 
            + window.location.hostname 
            + (window.location.port ? ':' + window.location.port : '');
        }
        return window.location.origin
    }
}

export default Utils