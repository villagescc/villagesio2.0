class Person{

    constructor(){
        this.personApi = new PersonApi();
        this.views = new ProductListViews($('#product_list'));
    }

    getPerson(){
        this.personApi.getPersonList()
            .then(data => data.forEach(item => this.views.update(item)))
            .catch(err => console.log(err))
    }

}
