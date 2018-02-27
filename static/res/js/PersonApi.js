class PersonApi{

    constructor(){
        this.http = new HttpService();
    }

    getPersonList(offset){
        return new Promise((resolve, reject) => {
            this.http.get('/product_infinite_scroll/'+offset)
                .then(data => resolve(data))
                .catch(err => reject(err));
        })
    }

}