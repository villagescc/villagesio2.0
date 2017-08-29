ALTER TABLE public.listings_listings ALTER COLUMN listing_type TYPE varchar(20) USING listing_type::varchar ;
ALTER TABLE public.listings_listings ALTER COLUMN listing_type SET NOT NULL ;
ALTER TABLE public.listings_listings ALTER COLUMN listing_type DROP DEFAULT ;