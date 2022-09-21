## Usage:

python main.py www.scale.com

output: www.scale.com.csv [company_name, company_logo_link]

## Problem statement:

Find customers of a company for a given url.

## Assumptions

- we have a list of urls representing companies whose customers we want to find (logo, company name)
- there are subpages on a given company's website that list or describe their customers (articles, case studies, list of names and logos, etc)
- we can get the html (either by direct get request or by rendering javascript single page applications)
- we can focus on english speaking world

Even if these assumptions all hold, the challenge remains hard to solve. 

## My Approach

I analyzed the source and noticed a couple of patterns that can be somewhat general.

- companies practice content marketing, thus they frequently post case studies about their clients
- companies use social proof to convince other similar customers to trust them. The most common is posting logos and names of well known companies on their website.
- many websites are built with CMS (Wordpress, Squarespace, etc). This means that html structures are similar, so we can use that to our advantage.
- there are some sitemap patterns we can use. For example subpages that contain lists of customers or case studies are typically domain/customers, domain/case_studie or similar.
- links to logos are typically in `<img>` tag
- company names are sometimes in alt attribute or somewhere "near" in the html tree (parent div or a) 
- page /customers is sometimes only a list, details (including logs) are one level deeper (/customers/customer_name)

I devised a simple algorithm that attempts to extract data using the above realizations. See limitations and future work at the end.


## How does it work?

First we try to detect the correct subpage that contains articles, list of logos, list of company names, etc. We do that by looking for `<a>` whose href contains certain keywords (customers, case studies).
If we find such a page we try to extract data (link to logo and customer company name). If we can't find such subpage we exit.

Second step, extraction, first tries to find `<img>` whose src attribute includes keywords (logo, Logo). 
If it finds such images (threshold is at least 3 - otherwise we assume we haven't found the right place yet), it extracts them and saves the data in csv file.
If it can't find such images, it assumes it is on a list subpage and needs to go one level deeper (try rippling.com).   
It tries to find `<a>` whose href contains keywords like 'customer', 'customers', etc.
If it still can't find anything useful it exists with an error.


### Tested on :

input of the first challenge
 * https://www.scale.com

input of the second challenge
 * https://amplitude.com 
 * https://www.pagerduty.com 
 * https://gusto.com  (doesn't work, because case studies have different url naming conventions)
 * https://www.rippling.com 

some companies that came to mind:
 * https://metabase.com 
 * https://posthog.com
 * https://mailchimp.com (it doesn't find anything because the case studies are with "influencers" in the field (no logos) only names and images of people
 * https://convertkit.com (same as above)


## How well it works?

My guesstimate is that this toy solution should work fine for companies similar to examples given - companies that do content marketing in the same way and use similar url structures and naming.
From my experience that holds for a sizable chunk of tech companies, b2b SaaS and similar. How many? 5% ? 20%? It's hard to say.

For better results we should come up with many such patterns and combine them.

## Pros and cons of this method

**Advantages of this approach are:**
- it's easy to get started; humans can detect simple patterns fairly quickly 
- patterns are easy to state and implement (few lines of code) 
- each pattern detection check is independent of each other, so it's fairly easy to parallelize detection

**Cons of this method are:**
- it's almost guaranteed that we'll miss a lot of simple and effective patterns
- humans are limited to a few dozens (hundreds?) of examples, so we'll miss many good pattern simply because we haven't encountered them
- it's hard to estimate the complexity of this approach O(number of patterns), because pattern detection code is arbitrarily hard to run

High-effort high-reward solution is to involve machine learning on a larger dataset to learn more patterns and creating a large decision tree that covers a larger percentage of cases. 


## Limitations and further improvements:

1. Current solution only works for websites in english (because of keyword detection hypothesis), however it should be fairly easy to extend it to other languages.

2. Keywords/urls that signal customers or logos can be anything. For example domain.com/clients currently doesn't work.

3. If we combined data from other datasets (that contain company names or logos) we could scan the whole website and only analyze subpages that are "heavy" with logo images and company names. 

4. Inconsistent naming of assets or names (logos, company name) are almost guaranteed. This solution has only the simplest workaround for those. Learning from structures (which are more consistent because of CMS use) is a better approach.



For example:

```
<ul>
   <li><img alt="Microsoft logo" src="microsoft_logo.png"/></li>
   <li><img alt="Google" src="google.png"/></li>
</ul>
```

This implementation would find one company (Microsoft) from the example above. If it could learn the structure of the website and recheck the html again, it would find another company (Google).

5. Sitemaps used for SEO are a well structured place to learn about the website structure and use that to do fewer requests and guessing. For example, if we find one case study we can assume siblings of that page could also contain useful data.

6. Paginated lists are currently not implemented, only the first page of customers if extracted (fairly easy to fix).

7. Customer company name search is not robust. More effort is needed to find names that are "near" the logo in the html tree.