class Person{

    constructor(){
        this.personApi = new PersonApi();
        this.views = new ProductListViews($('#product_list'));
    }

    getPerson(offset){
        this.personApi.getPersonList(offset)
            .then((data) => {
                data.forEach(item => this.views.update(item));
                initModals();
            })
            .catch(err => console.log(err))
    };

}
