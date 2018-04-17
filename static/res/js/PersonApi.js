class PersonApi{

    constructor(){
        this.http = new HttpService();
    }

    getPersonList(offset){
        return new Promise((resolve, reject) => {
            const pathname = location.pathname.split( 'home' ).pop().replace(/\//g, '');

            const params = new URLSearchParams(location.search);
            params.set('offset', offset);

            const scroll_url = '/product_infinite_scroll/' + pathname + '?' + params;
            this.http.get(scroll_url)
                .then(data => resolve(data))
                .catch(err => reject(err));
        })
    }

}