javascript:function iptxt() {
    var d = document;
    try {
        if (!d.body)throw(0);
        window.location = 'http://www.instapaper.com/text?u=' + encodeURIComponent(d.location.href);
    } catch (e) {
        alert('Please wait until the page has loaded.');
    }
}
iptxt();
void(0)

