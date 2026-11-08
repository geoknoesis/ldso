# Local ontology repairs and publication follow-up

These changes are in the working tree; the GitHub Pages deployment and w3id service have not been changed.

The Semantics ontology's nested multiline example quotes were repaired, and its `ent:` prefix is now declared. The six JSON-LD examples are regenerated from their Turtle counterparts with `python tools/sync_examples.py`; they previously included invalid JSON comments, stale terms, omitted triples, or differing literals. Turtle is now the canonical source for these example pairs.

Run `python -m pip install -r requirements-test.txt`, then `python -m unittest discover -s tests -v`. Checks cover all six ontology/shape/example sets, meta-SHACL, embedded Semantics Turtle examples, and RDF equivalence of each example pair. The GitHub Actions workflow runs the same checks when pushed. This does not prove full example conformance against every combined profile.

The tested `https://w3id.org/ldso/core`, `/core/1.0.0`, `/case`, and `/discovery` URLs returned 404 during the review. Direct GitHub Pages artifact URLs work. An offline catalog resolves the dependencies locally but does not repair HTTP redirects.

`publication/w3id/ldso/.htaccess` provides proposed redirects for the six existing, unversioned foundation endpoints. It must be tested under the w3id Apache configuration and submitted through the [w3id registration process](https://github.com/perma-id/w3id.org#creating-a-new-identifier). The contact/project information is in the adjacent README. No external request or publication has been submitted.

Before registering version routes, publish immutable, version-specific distributions. Do not route a fixed version IRI to a moving latest file. The current local patch is recorded separately from upstream commit `201dfe8f2733d23ee2e5fb90427215d3ac193012`; it has not been promoted to a normative foundation release. Case and Discovery need their own published distributions before their namespace routes can be activated.

Remaining release work: review and commit these local repairs, publish the repaired artifacts under an explicit release policy, verify RDF/HTML content negotiation and version routes, and activate tested redirect configuration in the external registry.
