class PersonApi{

    constructor(){
        this.http = new HttpService();
    }

    getPersonList(){
        return new Promise((resolve, reject) => {
            this.http.get('/product_infinite_scroll/10')
                .then(data => resolve(data))
                .catch(err => reject(err))
        })
    }

}