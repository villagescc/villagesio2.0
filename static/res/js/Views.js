class Views{

    constructor(element){
        this.element = element;
    }

    update(data){
        this.element.append(this.template(data))
    }

    template(data){
        throw new Error('this method cannot be initialized')
    }
}

class PersonListViews extends Views{

    constructor(element){
        super(element)
    }

    template(data){
        return `
            <div class="col-12">
              <div class="person-box">
                <div class="avatar-wrapper blue">
                  <img src="/static/res/img/people/${data.image}.png" alt="avatar">
                </div>
    
                <div class="person-id">
                  <h1>${data.fullname}</h1>
                  <div class="tag-container">                  
                    ${data['tags'].map(item => `
                        <a class="tag" href="#">${item}</a>
                    `)}
                  </div> 
                </div>
        
                <div class="price-container">
                      <img src="new_template/res/img/icons/balance_b.png" alt="balance">
                      <span class="price">${data.price} hours</span>
                </div>
    
                <div class="like-container">
                  <img src="new_template/res/img/icons/heart_b.png" alt="balance">
                  <span class="like-count">${data.likes} Hearts</span>
                </div>
    
                <div class="location-container">
                  <img src="new_template/res/img/icons/map_b.png" alt="location">
                  <span class="location">${data.address}</span>
                </div>
    
                <div class="date-container">
                  <img src="/static/res/img/icons/calendar_b.png" alt="date">
                  <span class="date">${data.date}</span>
                </div>
    
                <div class="person-action">
                  <a class="action-menu-item" href="#"><img src="/static/res/img/icons/heart.png" alt="like"></a>
                  <a class="action-menu-item" href="#"><img src="/static/res/img/icons/wallet.png" alt="buy"></a>
                  <a class="action-menu-item" href="#"><img src="/static/res/img/icons/mail.png" alt="contact"></a>
                </div>
              </div>
            </div>
        `;
    }

}

class ProductListViews extends Views {

    constructor(element){

        super(element)
    }

    template(data){
        return data ? data : ''
    }
}

