class Person{

    constructor(){
        this.personApi = new PersonApi();
        this.views = new ProductListViews($('#product_list'));
    }

    getPerson(offset){
        this.personApi.getPersonList(offset)
            .then((data) => {
                this.views.update(data);
                initModals();
            })
            .catch(err => console.log(err))
    };

}
