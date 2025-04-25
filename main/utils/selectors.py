SELECTORS = {
    "region": {
        "list": ".venuesCitiesList",
        "link": ".venuesCitiesList__link",
    },
    "venues": {
        # List venue pages (region-based)
        "venue_list_item": "li.vendorTile",
        "venue_name": "div.vendorTile__content h2",
        "venue_rating": "span.vendorTile__rating",
        "venue_rating_text": "div.vendorTile__contentRating",
        "venue_location": "span.vendorTile__location",
        "venue_link": "a",
        "venue_price_block": "div.vendorTileFooter__price",
        "venue_price_icon": "div.vendorTileFooter__price i",
        "venue_capacity": "div.vendorTileFooter__capacity",

        # Detail venue selectors
        "details": {
            "description": "div.storefrontDescription__content.app-storefront-description-readMore",
            "address": "div.storefrontAddresses__header",
            "venue_url": "span.storefrontHeadingWebsite__label.app-storefront-visit-website",
            "map_url": "a.storefrontAddresses__openMap",
            "social_links": "div.storefrontSummarySocial__list a",
            "deals_section": {
                    "tile": "div.storefrontDealsTile",
                    "type": ".storefrontDealsTile__category",
                    "title": ".storefrontDealsTile__text",
                    "expires_on": ".storefrontDealsTile__time"
                    },

            "faq_sections": {
                    "venue_type_tags": "Venue type",
                    "dining_options": "Dining options",
                    "ceremony_options": "Ceremony options",
                    "entertainment_options": "Evening entertainment"
                    },
            "suppliers_section": {
                    "tile": "div.storefrontEndorsedVendor__tile",
                    "link": "a.storefrontEndorsedVendor__tileTitle",
                    "image": "picture img",
                    "rating": "span.storefrontEndorsedVendor__rating",
                    "info": "div.storefrontEndorsedVendor__info"
                    }
                    }
    }
}