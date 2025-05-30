/**
* Gère le système de pagination d'un composant
* param elementPerPageId : Nom de la liste déroulante contenant le nombre de pages à afficher
* param paginationBaseId [OPTIONNEL A RENSEIGNER] : Préfixe de l'id des boutons du navbar
* param filteredElementClassName [OPTIONNEL] : Nom de la classe donnée aux éléments à filtrer
*                                              grâce au système de filtrage intégré
* param navbarPaginationContainerId : id de l'emplacement où placer la navbar de la pagination
* param listElementClassName : Nom de la classe associée à tous les éléments à paginer
* 
*/
function paginatorHandler(elementPerPageId, paginationBaseId = "pagination-btn", 
	filteredElementClassName="", 
	navbarPaginationContainerId, listElementClassName) {
		
	var ELEMENT_PER_PAGE = $(`#${elementPerPageId}`).find(":selected").val();
	var ELEMENT_PER_PAGE_ID = elementPerPageId;
	var PAGINATION_BASE_ID = paginationBaseId;
	var FILTERED_ELEMENT_CLASS_NAME= filteredElementClassName;
	var NAVBAR_PAGINATION_CONTAINER_ID = navbarPaginationContainerId;
	var LIST_ELEMENT_CLASS_NAME = listElementClassName;
	
	var listData = []; // Contient toutes les données de la liste
	
	var currentPage = 1; // Par défaut 
	
	/**
	* Permet de récupérer les données HTML du tableau d'éléments à paginer
	* return : toutes les données du filtre (filtrées si besoin)  
	*/
	function getListData() {
		
		/* /!\ IMPORTANT /!\       
		* Ce code permet de récupérer toute donnée ayant été filtrée
		* par le code de recherche d'éléments. Il y a donc une forme de
		* dépendance entre ce code de pagination et celui qui a pour
		* but de gérer le filtrage de données. 
		*/
		
		listData = [];
		$(`.${listElementClassName}`).each(function() {
			if (!$(this).hasClass(FILTERED_ELEMENT_CLASS_NAME)
				&& !$(this).hasClass("empty-form")) { // Problème causé par les inlines paginés
				listData.push($(this).prop('outerHTML'))
				
			}
		})  
		console.log(listData)
		return listData;
	}
	
	/**
	* Donne le nombre de pages à gérer pour paginer
	* return : un nombre entier positif représentant le nombre de pages nécessaires
	*/
	function getNumberOfPages() {
		getListData()
		return Math.ceil(listData.length / ELEMENT_PER_PAGE);
	}
	
	/**
	* Gère l'entièreté de l'affichage de la page courante liée
	* à la pagination
	*/
	function showMatchingPage() {
		
		if (getListData().length == 0) {
			$(`#${NAVBAR_PAGINATION_CONTAINER_ID}`).html(getPaginationNav());
		} else if (currentPage >= 1 && currentPage <= getNumberOfPages()) {
			// Affiche la barre de pagination
			// On récupère les données associées à la page
			toShowData = getListData().splice(ELEMENT_PER_PAGE * (currentPage - 1), 
			ELEMENT_PER_PAGE);
			
			// Affiche / Cache les données en fonction de la page courante
			$(`.${listElementClassName}`).each(function() {
				if (jQuery.inArray($(this).prop('outerHTML'), toShowData) > -1) {   
					$(this).removeClass("out-of-pagination");
				} else {
					$(this).addClass("out-of-pagination");
				}
			})
			
			// Affiche la barre de pagination
			$(`#${NAVBAR_PAGINATION_CONTAINER_ID}`).html(getPaginationNav());
			bindPaginationButtons()
			$(`#total-paginated-elements`).html(getListData().length)
			
			// S'assure de ne pas avoir des duplications de données
			toShowData = []
		}
	}
	
	/**
	* Gère le binding des boutons du navbar de la pagination
	*/
	function bindPaginationButtons() {
		
		if (getListData().length > 0) {
			
			// On bind les boutons de navigation gauche et droite
			
			// On s'assure de ne pas binder plusieurs fois l'item
			$(document).off("click", `#${PAGINATION_BASE_ID}-prev`)
			if (currentPage > 1) { 
				// Si on est pas à la 1ere page, le btn prev renvoi en arrière
				$(document).on("click" ,`#${PAGINATION_BASE_ID}-prev` ,function() {
					currentPage--;
					showMatchingPage()
				})
			} else {
				$(`#${PAGINATION_BASE_ID}-prev`).addClass("disabled-pagination-btn");
			}
			
			// On s'assure de ne pas binder plusieurs fois l'item
			$(document).off("click", `#${PAGINATION_BASE_ID}-next`)
			if (currentPage < getNumberOfPages()) {
				// Si on est pas à la dernière page, le btn next envoi sur la page suivante
				$(document).on("click" ,`#${PAGINATION_BASE_ID}-next` ,function() {
					currentPage++;
					showMatchingPage()          
				})
			} else {
				$(`#${PAGINATION_BASE_ID}-next`).addClass("disabled-pagination-btn");
			}
			
			// On bind les boutons numérotés
			$(".bindable-nav-btn").each(function() {
				$(this).off("click"); // Pour ne pas doubler les binds
				$(this).on("click", function() {
					// Redirige vers la page du numéro
					currentPage = parseInt($(this).text())
					showMatchingPage()          
					
				});
				
			})
		} else {
			console.error('Aucune donnée à afficher pour la pagination.');
		}
	}
	
	// On initialise la pagination (ici, current_page = 1)
	showMatchingPage()
	
	// Dès que l'utilisateur lâche une touche sur la zone de saisi (keyup)
	$("#search-bar-input").on("keyup", function() { 
		// Ici, $(this) représente la barre de recherche de la liste
		
		var value = $(this).val().toLowerCase(); // Valeur de la barre de recherche
		$(`.${listElementClassName}`).each(function() { // Permet d'itérer dans la table des éléments de liste (List Filter)
			// Ici, $(this) représente un élément de la liste (filter fait comme un parcours de liste)
			
			if ($(this).text() // Récupère le nom de la donnée affichée parcouru dans la liste
			.toLowerCase() // La met en lowercase
			.indexOf(value) > -1) {
				
				$(this).removeClass(FILTERED_ELEMENT_CLASS_NAME);
			} else {
				$(this).addClass(FILTERED_ELEMENT_CLASS_NAME);
				
			}
			// -- EXPLICATION DU indexOf() --
			// "a".indexOf("b") => -1 car "a" ne contient pas "b" mais
			// "fabrice".indexOf("b") => 2 car la 1ere occurrence de "b" est en indice 2
			
		});
		currentPage = 1;
		// $(this) change car pour chaque cas, on associe à this 
		// "l'élément" modifiable de la fonction anonyme
		
		showMatchingPage();
	});
	
	$("#paginator-page-selector").on("keyup", function() {
		selectedPage = $(this).val();
		if (selectedPage.length == 0) {
			// Plus rien n'est saisi dans la barre de recherche 
			currentPage = 1
			showMatchingPage();
			
		} else if (jQuery.type(parseInt(selectedPage)) === "number") {
			// On change de page si la donnée est un nombre
			
			// Si on donne un trop grand nombre, on obtient la dernière page
			currentPage = parseInt(selectedPage) > getNumberOfPages() ? getNumberOfPages() // On dépasse le nombre de pages 
			: parseInt(selectedPage); // On va à la page donnée
			showMatchingPage();
		} 
	})
	
	// Quand on décide de changer le nombre de pages
	$(`#${ELEMENT_PER_PAGE_ID}`).on("change", function() {
		ELEMENT_PER_PAGE = $(`#${elementPerPageId}`).find(":selected").val();
		currentPage = 1
		showMatchingPage();
	})
	
	/**
	* Affiche la navbar de la page courante
	* return : Une chaine de caractères représentant la navbar en HTML
	*/
	function getPaginationNav() {
		
		// Le conteneteditable empêche tout le texte d'être sélectionné
		let navBar = "<ul id='pagination-navbar' conteneteditable='false'>";
		let numberOfPage = getNumberOfPages();
		
		// Bouton pour aller sur la page précédente
		navBar += `<li id="${PAGINATION_BASE_ID}-prev" class="btn-list-filter-pagination-nav">‹</li>`;
		
		if (numberOfPage > 8) {
			// Cas où la pagination gère beaucoup de données
			
			// Permet d'afficher les pages qui débutent la pagination
			for (let pageNumber = 0; pageNumber <= 3; pageNumber++) {
				if (pageNumber >= 1 && pageNumber <= numberOfPage) {
					navBar += `<li id="${PAGINATION_BASE_ID}-${pageNumber}" class="btn-list-filter-pagination-nav bindable-nav-btn`;
					navBar += pageNumber == currentPage ? " active-pagination-page" : "";
					navBar += `">${pageNumber}</li>`
				}
			}
			
			if (currentPage - 4 > 0) {
				navBar += `<li class="elt-list-filter-pagination-nav">...</li>`;
			}
			
			// Permet d'afficher la page courante
			if (currentPage + 2 < numberOfPage && currentPage - 3 > 0) {
				
				navBar += `<li id="${PAGINATION_BASE_ID}-${currentPage}" class="btn-list-filter-pagination-nav bindable-nav-btn active-pagination-page`;
				navBar += `">${currentPage}</li>`
			}
			
			if (currentPage + 3 < numberOfPage) {
				navBar += `<li class="elt-list-filter-pagination-nav">...</li>`;
			}
			
			// Permet d'afficher les pages qui terminent la pagination
			for (let pageNumber = Math.ceil(numberOfPage) - 2; pageNumber <= numberOfPage; pageNumber++) {
				if (pageNumber >= 1 && pageNumber <= numberOfPage) {
					navBar += `<li id="${PAGINATION_BASE_ID}-${pageNumber}" class="btn-list-filter-pagination-nav bindable-nav-btn`;
					navBar += pageNumber == currentPage ? " active-pagination-page" : "";
					navBar += `">${pageNumber}</li>`
				}
			}
		} else {
			for (let pageNumber = 1; pageNumber <= numberOfPage; pageNumber++) {
				navBar += `<li id="${PAGINATION_BASE_ID}-${pageNumber}" class="btn-list-filter-pagination-nav bindable-nav-btn`;
				navBar += pageNumber == currentPage ? " active-pagination-page" : "";
				navBar += `">${pageNumber}</li>`
			} 
		}
		
		// Bouton pour aller sur la page suivante
		navBar += `<li id="${PAGINATION_BASE_ID}-next" class="btn-list-filter-pagination-nav">›</li>`;
		
		navBar += "</ul>";
		
		return navBar;
	}
}