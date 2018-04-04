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
        return `
            <div class="col-12 col-sm-6 col-md-12 col-lg-6 col-xl-4 col-xxl-3" id="div_listing_${data.profile_username}">

              <div class="post-box">

                <div class="post-cover listing-modal" style="background-image: url('${data.product_image}');" data-listing-id="${data.listing_id}">
                  <span class="type">${data.listing_type}</span>
                  <span class="price">${data.price} VH</span>

                </div>

                <div class="post-content listing-modal" data-listing-id="${data.listing_id}">
                  <div class="avatar-thumbnail" style="background-image: url('${data.profile_image}');">
                    <!--<img class="trusted-icon" src="/static/new_template/res/img/icons/trusted-icon.png"-->
                         <!--alt="trusted">-->
                  </div>

                  <h1>${data.title}</h1>
                  <p>${data.description}</p>
                  <div class="tag-container">
                      ${data['tags'].map(item => `
                          <a class="tag" href="#">${item.name}</a>
                      `)}
                  </div>

                </div>

                <div class="post-action">

                  <a class="action-menu-item trust-modal" data-profile-username="${data.profile_username}" href="/trust/${data.profile_username}"><img src="/static/new_template/res/img/icons/heart.png" alt="like"></a>
                  <a class="action-menu-item payment-modal" data-profile-username="${data.profile_username}"><img src="/static/new_template/res/img/icons/wallet.png" alt="buy"></a>
                  <a class="action-menu-item contact-modal" data-profile-username="${data.profile_username}"
                     data-listing-title="${data.title}" href="#"><img src="/static/new_template/res/img/icons/mail.png" alt="contact"></a>

                </div>

              </div>

            </div>
        `
    }
}

